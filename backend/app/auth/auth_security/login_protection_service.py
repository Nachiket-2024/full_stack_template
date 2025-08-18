# ---------------------------- External Imports ----------------------------
# For logging
import logging

# For traceback
import traceback

# ---------------------------- Internal Imports ----------------------------
# Redis client for tracking failed login attempts
from ...redis.client import redis_client

# Load configuration values from settings
from ...core.settings import settings

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Login Protection Service ----------------------------
class LoginProtectionService:
    """
    Service to prevent brute-force login attempts by tracking failed logins.
    Locks account temporarily after repeated failed attempts.
    """

    # ---------------------------- Configurable Values ----------------------------
    MAX_FAILED_LOGIN_ATTEMPTS: int = settings.MAX_FAILED_LOGIN_ATTEMPTS
    LOGIN_LOCKOUT_TIME: int = settings.LOGIN_LOCKOUT_TIME                

    # ---------------------------- Record Failed Attempt ----------------------------
    @staticmethod
    async def record_failed_attempt(key: str) -> None:
        """
        Increment failed login counter for the given key (user/email/IP).
        """
        try:
            count = await redis_client.get(key)
            if count is None:
                await redis_client.set(key, 1, ex=LoginProtectionService.LOGIN_LOCKOUT_TIME)
            else:
                await redis_client.incr(key)
        except Exception:
            logger.error("Error recording failed login attempt:\n%s", traceback.format_exc())

    # ---------------------------- Check If Locked ----------------------------
    @staticmethod
    async def is_locked(key: str) -> bool:
        """
        Check if the account/IP is currently locked due to repeated failures.
        """
        try:
            count = await redis_client.get(key)
            if count is not None and int(count) >= LoginProtectionService.MAX_FAILED_LOGIN_ATTEMPTS:
                return True
            return False
        except Exception:
            logger.error("Error checking login lock status:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Reset Failed Attempts ----------------------------
    @staticmethod
    async def reset_failed_attempts(key: str) -> None:
        """
        Reset the failed login counter after successful login.
        """
        try:
            await redis_client.delete(key)
        except Exception:
            logger.error("Error resetting failed login attempts:\n%s", traceback.format_exc())

# ---------------------------- Service Instance ----------------------------
# Single instance for global use
login_protection_service = LoginProtectionService()
