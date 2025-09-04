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

# ---------------------------- Rate Limiter Service ----------------------------
# Service class for implementing rate limiting on endpoints
class RateLimiterService:

    # ---------------------------- Configurable Values ----------------------------
    # Maximum allowed requests per time window
    MAX_REQUESTS_PER_WINDOW: int = settings.MAX_REQUESTS_PER_WINDOW
    # Duration of the time window in seconds
    REQUEST_WINDOW_SECONDS: int = settings.REQUEST_WINDOW_SECONDS

    # ---------------------------- Record Request ----------------------------
    # Track a request in Redis and check if it exceeds the allowed limit
    @staticmethod
    async def record_request(key: str) -> bool:

        try:
            # Retrieve current request count from Redis
            count = await redis_client.get(key)
            if count is None:
                # First request: set key with expiration
                await redis_client.set(key, 1, ex=RateLimiterService.REQUEST_WINDOW_SECONDS)
                return True
            elif int(count) < RateLimiterService.MAX_REQUESTS_PER_WINDOW:
                # Increment request count if under limit
                await redis_client.incr(key)
                return True
            else:
                # Deny if request count exceeds limit
                return False
        except Exception:
            # Log any errors while recording requests
            logger.error("Error recording rate-limited request:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Reset Counter ----------------------------
    # Reset request count for a given key
    @staticmethod
    async def reset_counter(key: str) -> None:

        try:
            # Delete the Redis key to reset counter
            await redis_client.delete(key)
        except Exception:
            # Log errors during counter reset
            logger.error("Error resetting rate limiter counter:\n%s", traceback.format_exc())

    # ---------------------------- Decorator for Endpoints ----------------------------
    # Decorator to apply rate limiting to FastAPI endpoint functions
    def rate_limited(self, endpoint_name: str):

        def decorator(func):
            # Wrapper function to enforce rate limiting
            @wraps(func)   # Preserve original function signature
            async def wrapper(*args, **kwargs):

                # Find FastAPI Request object in args or kwargs
                request: Request | None = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                if not request:
                    # Attempt to get Request from keyword arguments
                    request = kwargs.get("request", None)

                # Extract client IP, default to "unknown" if missing
                ip_address = request.client.host if request else "unknown"

                # Build Redis key combining endpoint and IP
                key = f"{endpoint_name}:{ip_address}"
                # Check if the request is allowed
                allowed = await self.record_request(key)

                # Deny request if rate limit exceeded
                if not allowed:
                    return JSONResponse(
                        content={"error": f"Too many {endpoint_name} attempts"},
                        status_code=429
                    )

                # Proceed with original endpoint call
                return await func(*args, **kwargs)
            return wrapper
        return decorator


# ---------------------------- Service Instance ----------------------------
# Single global instance of the RateLimiterService
rate_limiter_service = RateLimiterService()
