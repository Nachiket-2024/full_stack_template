# ---------------------------- External Imports ----------------------------
# Logging module for tracking events and errors
import logging

# Module to capture detailed exception stack traces
import traceback

# ---------------------------- Internal Imports ----------------------------
# Redis client for tracking failed login attempts and lockouts
from ...redis.client import redis_client

# Load configuration values like max attempts and lockout time
from ...core.settings import settings

# ---------------------------- Logger Setup ----------------------------
# Initialize a logger specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Login Protection Service ----------------------------
# Service class to protect against brute-force login attempts
class LoginProtectionService:

    # ---------------------------- Configurable Values ----------------------------
    # Maximum allowed failed login attempts before lockout
    MAX_FAILED_LOGIN_ATTEMPTS: int = settings.MAX_FAILED_LOGIN_ATTEMPTS
    # Lockout duration in seconds
    LOGIN_LOCKOUT_TIME: int = settings.LOGIN_LOCKOUT_TIME                

    # ---------------------------- Record Failed Attempt ----------------------------
    # Increment failed login attempts count in Redis
    @staticmethod
    async def record_failed_attempt(key: str) -> None:

        try:
            count = await redis_client.get(key)
            if count is None:
                # First failure: set key with expiration
                await redis_client.set(key, 1, ex=LoginProtectionService.LOGIN_LOCKOUT_TIME)
            else:
                # Increment existing count
                await redis_client.incr(key)
        except Exception:
            # Log errors if Redis operation fails
            logger.error("Error recording failed login attempt:\n%s", traceback.format_exc())

    # ---------------------------- Check If Locked ----------------------------
    # Determine if a user is currently locked out based on failed attempts
    @staticmethod
    async def is_locked(key: str) -> bool:

        try:
            count = await redis_client.get(key)
            # Lock if count exceeds or equals maximum allowed attempts
            if count is not None and int(count) >= LoginProtectionService.MAX_FAILED_LOGIN_ATTEMPTS:
                return True
            return False
        except Exception:
            # Log any errors while checking lock status
            logger.error("Error checking login lock status:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Reset Failed Attempts ----------------------------
    # Clear failed attempts count after successful login
    @staticmethod
    async def reset_failed_attempts(key: str) -> None:

        try:
            await redis_client.delete(key)
        except Exception:
            # Log any errors during reset
            logger.error("Error resetting failed login attempts:\n%s", traceback.format_exc())

    # ---------------------------- Helper: Attempted Action ----------------------------
    # Record action outcome and enforce lockout if necessary
    @staticmethod
    async def check_and_record_action(key: str, success: bool) -> bool:

        # Deny action if currently locked
        if await LoginProtectionService.is_locked(key):
            return False
        # Reset failed attempts on success
        if success:
            await LoginProtectionService.reset_failed_attempts(key)
        else:
            # Record failed attempt on failure
            await LoginProtectionService.record_failed_attempt(key)
        return True


# ---------------------------- Service Instance ----------------------------
# Single global instance for login protection usage
login_protection_service = LoginProtectionService()
