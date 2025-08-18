# ---------------------------- External Imports ----------------------------
# For logging
import logging

# For traceback
import traceback

# ---------------------------- Internal Imports ----------------------------
# Redis client for tracking requests
from ...redis.client import redis_client

# Load configuration values from settings
from ...core.settings import settings

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Rate Limiter Service ----------------------------
class RateLimiterService:
    """
    Service to prevent excessive requests per user/IP.
    Can be used for endpoints like login, password reset, or signup.
    """

    # ---------------------------- Configurable Values ----------------------------
    MAX_REQUESTS_PER_WINDOW: int = settings.MAX_REQUESTS_PER_WINDOW   
    REQUEST_WINDOW_SECONDS: int = settings.REQUEST_WINDOW_SECONDS     

    # ---------------------------- Record Request ----------------------------
    @staticmethod
    async def record_request(key: str) -> bool:
        """
        Record a request for the given key (user/email/IP).
        Returns True if request is allowed, False if rate limit exceeded.
        """
        try:
            count = await redis_client.get(key)
            if count is None:
                await redis_client.set(key, 1, ex=RateLimiterService.REQUEST_WINDOW_SECONDS)
                return True
            elif int(count) < RateLimiterService.MAX_REQUESTS_PER_WINDOW:
                await redis_client.incr(key)
                return True
            else:
                return False
        except Exception:
            logger.error("Error recording rate-limited request:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Reset Counter ----------------------------
    @staticmethod
    async def reset_counter(key: str) -> None:
        """
        Reset the counter for a given key, e.g., after a successful request or admin override.
        """
        try:
            await redis_client.delete(key)
        except Exception:
            logger.error("Error resetting rate limiter counter:\n%s", traceback.format_exc())

# ---------------------------- Service Instance ----------------------------
# Single instance for global use
rate_limiter_service = RateLimiterService()
