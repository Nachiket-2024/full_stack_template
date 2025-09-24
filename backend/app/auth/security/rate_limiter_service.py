# ---------------------------- External Imports ----------------------------
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

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Rate Limiter Service Class ----------------------------
# Service class for implementing rate limiting on endpoints
class RateLimiterService:
    """
    1. record_request - Track a request and enforce max requests per time window.
    2. reset_counter - Reset request counter for a given key.
    3. rate_limited - Decorator to apply rate limiting to FastAPI endpoint functions.
    """

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
            2. Initialize key with 1 and expiration if not existing.
            3. Increment count if under max allowed requests.
            4. Deny request if count exceeds maximum.
            5. Return True if request allowed, False if denied or error occurs.

        Output:
            1. bool: True if request allowed, False if rate limit exceeded or error occurs.
        """
        try:
            # Step 1: Retrieve current request count from Redis
            count = await redis_client.get(key)

            # Step 2: Initialize key with 1 and expiration if not existing
            if count is None:
                await redis_client.set(key, 1, ex=RateLimiterService.REQUEST_WINDOW_SECONDS)
                return True  # Step 5: Return True if request allowed

            # Step 3: Increment count if under max allowed requests
            elif int(count) < RateLimiterService.MAX_REQUESTS_PER_WINDOW:
                await redis_client.incr(key)
                return True  # Step 5: Return True if request allowed

            # Step 4: Deny request if count exceeds maximum
            else:
                return False  # Step 5: False if denied or error occurs

        except Exception:
            # Log exception with full traceback
            logger.error("Error recording rate-limited request:\n%s", traceback.format_exc())
            return False  # Step 5: False if denied or error occurs

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
            # Step 1: Delete the Redis key to reset the request counter
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
            1. Define decorator function.
            2. Wrap endpoint function to extract client IP and build Redis key.
            3. Call record_request to check if request is allowed.
            4. Return 429 JSONResponse if rate limit exceeded inside wrapper.
            5. Proceed with original endpoint function if allowed.
            6. Return wrapper function as decorated endpoint.
            7. Return decorator function to apply rate limiting.

        Output:
            1. Function wrapper enforcing rate limiting on the endpoint.
        """
        # Step 1: Define decorator function
        def decorator(func):
            # Step 2: Wrap endpoint function to enforce rate limiting
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Step 2a: Initialize Request object as None
                request: Request | None = None

                # Step 2b: Loop through positional arguments to find Request object
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

                # Step 2c: Attempt to get Request from keyword arguments if not found
                if not request:
                    request = kwargs.get("request", None)

                # Step 2d: Extract client IP, defaulting to "unknown"
                ip_address = request.client.host if request else "unknown"

                # Step 2e: Build Redis key using endpoint name and client IP
                key = f"{endpoint_name}:{ip_address}"

                # Step 3: Call record_request to check if request is allowed
                allowed = await self.record_request(key)

                # Step 4: Return 429 JSONResponse if rate limit exceeded
                if not allowed:
                    return JSONResponse(
                        content={"error": f"Too many {endpoint_name} attempts"},
                        status_code=429
                    )

                # Step 5: Proceed with original endpoint function if allowed
                return await func(*args, **kwargs)

            # Step 6: Return wrapper function as decorated endpoint
            return wrapper

        # Step 7: Return decorator function to apply rate limiting
        return decorator


# ---------------------------- Service Instance ----------------------------
# Single global instance of the RateLimiterService
rate_limiter_service = RateLimiterService()
