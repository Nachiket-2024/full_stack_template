# ---------------------------- External Imports ----------------------------
# Logging module for tracking events and errors
import logging

# Module to capture detailed exception stack traces
import traceback

# Utility to preserve function metadata in decorators
from functools import wraps

# FastAPI Request object for handling incoming HTTP requests
from fastapi import Request

# FastAPI JSONResponse for sending structured HTTP responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Redis client for tracking request counts for rate limiting
from ...redis.client import redis_client

# Load configuration values like max requests and time windows
from ...core.settings import settings

# ---------------------------- Logger Setup ----------------------------
# Initialize a logger specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Rate Limiter Service Class ----------------------------
# Service class for implementing rate limiting on endpoints
class RateLimiterService:
    """
    1. record_request - Track a request and enforce max requests per time window.
    2. reset_counter - Reset request counter for a given key.
    3. rate_limited - Decorator to apply rate limiting to FastAPI endpoint functions.
    """

    # ---------------------------- Configurable Values ----------------------------
    # Maximum allowed requests per time window
    MAX_REQUESTS_PER_WINDOW: int = settings.MAX_REQUESTS_PER_WINDOW
    # Duration of the time window in seconds
    REQUEST_WINDOW_SECONDS: int = settings.REQUEST_WINDOW_SECONDS

    # ---------------------------- Record Request ----------------------------
    @staticmethod
    async def record_request(key: str) -> bool:
        """
        Input:
            1. key (str): Redis key combining endpoint and client IP.

        Process:
            1. Retrieve current request count from Redis.
            2. If key does not exist, set to 1 with expiration.
            3. Increment count if under max allowed requests.
            4. Deny if count exceeds max requests.

        Output:
            1. bool: True if request allowed, False if rate limit exceeded or error occurs.
        """
        try:
            # Get current request count from Redis
            # Retrieve Redis key value
            count = await redis_client.get(key)

            # Check if this is the first request
            if count is None:
                # Set initial count to 1 and set expiration for window
                await redis_client.set(key, 1, ex=RateLimiterService.REQUEST_WINDOW_SECONDS)
                # Allow request
                return True

            # Check if current count is under maximum allowed
            elif int(count) < RateLimiterService.MAX_REQUESTS_PER_WINDOW:
                # Increment request count
                await redis_client.incr(key)
                # Allow request
                return True

            # If count exceeds maximum allowed requests
            else:
                # Deny request
                return False

        # Catch exceptions from Redis operations
        except Exception:
            # Log exception with full traceback
            logger.error("Error recording rate-limited request:\n%s", traceback.format_exc())
            # Deny request on error
            return False

    # ---------------------------- Reset Counter ----------------------------
    @staticmethod
    async def reset_counter(key: str) -> None:
        """
        Input:
            1. key (str): Redis key for endpoint + client IP.

        Process:
            1. Delete the Redis key to reset the request counter.

        Output:
            1. None
        """
        try:
            # Delete Redis key to reset counter
            await redis_client.delete(key)
        except Exception:
            # Log any error encountered
            logger.error("Error resetting rate limiter counter:\n%s", traceback.format_exc())

    # ---------------------------- Decorator for Endpoints ----------------------------
    def rate_limited(self, endpoint_name: str):
        """
        Input:
            1. endpoint_name (str): Name of the endpoint being rate-limited.

        Process:
            1. Wrap the endpoint function to extract client IP.
            2. Build Redis key using endpoint and IP.
            3. Call record_request to check if allowed.
            4. Return 429 JSONResponse if rate limit exceeded.
            5. Proceed with original endpoint function if allowed.

        Output:
            1. Function wrapper enforcing rate limiting on the endpoint.
        """
        # Define decorator function
        def decorator(func):
            # Wrap endpoint function to enforce rate limiting
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Initialize Request object as None
                request: Request | None = None

                # Loop through positional arguments to find Request object
                for arg in args:
                    if isinstance(arg, Request):
                        # Assign found Request
                        request = arg
                        # Stop searching
                        break

                # Attempt to get Request from keyword arguments if not found
                if not request:
                    request = kwargs.get("request", None)

                # Extract client IP, defaulting to "unknown" if missing
                ip_address = request.client.host if request else "unknown"

                # Build Redis key using endpoint name and client IP
                key = f"{endpoint_name}:{ip_address}"

                # Check if request is allowed under rate limiting
                allowed = await self.record_request(key)

                # Deny request if limit exceeded
                if not allowed:
                    # Return HTTP 429 with JSON message
                    return JSONResponse(
                        content={"error": f"Too many {endpoint_name} attempts"},
                        status_code=429
                    )

                # Proceed with original endpoint function
                return await func(*args, **kwargs)

            # Return the wrapper function
            return wrapper

        # Return decorator function
        return decorator


# ---------------------------- Service Instance ----------------------------
# Single global instance of the RateLimiterService
rate_limiter_service = RateLimiterService()
