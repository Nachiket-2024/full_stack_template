# ---------------------------- External Imports ----------------------------
# Module to capture detailed exception stack traces
import traceback

# ---------------------------- Internal Imports ----------------------------
# Redis client for tracking failed login attempts and lockouts
from ...redis.client import redis_client

# Load configuration values like max attempts and lockout time
from ...core.settings import settings

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Login Protection Service Class ----------------------------
# Service class to protect against brute-force login attempts
class LoginProtectionService:
    """
    1. record_failed_attempt - Increment failed login attempts count in Redis.
    2. is_locked - Check if user is currently locked out due to too many failed attempts.
    3. reset_failed_attempts - Clear failed attempts after successful login.
    4. check_and_record_action - Record action outcome and enforce lockout if necessary.
    """

    # Maximum allowed failed login attempts before lockout
    MAX_FAILED_LOGIN_ATTEMPTS: int = settings.MAX_FAILED_LOGIN_ATTEMPTS

    # Lockout duration in seconds
    LOGIN_LOCKOUT_TIME: int = settings.LOGIN_LOCKOUT_TIME                

    # ---------------------------- Record Failed Attempt ----------------------------
    @staticmethod
    async def record_failed_attempt(key: str) -> None:
        """
        Input:
            1. key (str): Redis key for tracking failed login attempts.

        Process:
            1. Retrieve current failure count from Redis.
            2. If no existing count, initialize key with 1 and expiration.
            3. Otherwise, increment existing failure count.

        Output:
            1. None
        """
        try:
            # Step 1: Retrieve current failure count from Redis
            count = await redis_client.get(key)

            # Step 2: If no existing count, initialize key with 1 and expiration
            if count is None:
                await redis_client.set(key, 1, ex=LoginProtectionService.LOGIN_LOCKOUT_TIME)
            else:
                # Step 3: Otherwise, increment existing failure count
                await redis_client.incr(key)

        except Exception:
            # Log the exception with full traceback
            logger.error("Error recording failed login attempt:\n%s", traceback.format_exc())

    # ---------------------------- Check If Locked ----------------------------
    @staticmethod
    async def is_locked(key: str) -> bool:
        """
        Input:
            1. key (str): Redis key for tracking failed login attempts.

        Process:
            1. Retrieve current failure count from Redis.
            2. Compare count with maximum allowed failed attempts.

        Output:
            1. bool: True if user is locked, False otherwise.
        """
        try:
            # Step 1: Retrieve current failure count from Redis
            count = await redis_client.get(key)

            # Step 2: Compare count with maximum allowed failed attempts
            if count is not None and int(count) >= LoginProtectionService.MAX_FAILED_LOGIN_ATTEMPTS:
                return True  # User is locked

            return False  # User is not locked

        except Exception:
            # Log exception with full traceback
            logger.error("Error checking login lock status:\n%s", traceback.format_exc())
            
            return False  # Default to unlocked on error

    # ---------------------------- Reset Failed Attempts ----------------------------
    @staticmethod
    async def reset_failed_attempts(key: str) -> None:
        """
        Input:
            1. key (str): Redis key for failed login attempts.

        Process:
            1. Delete key from Redis to reset failure count.

        Output:
            1. None
        """
        try:
            # Step 1: Delete key from Redis to reset failure count
            await redis_client.delete(key)

        except Exception:
            # Log exception with full traceback
            logger.error("Error resetting failed login attempts:\n%s", traceback.format_exc())

    # ---------------------------- Check and Record Action ----------------------------
    @staticmethod
    async def check_and_record_action(key: str, success: bool) -> bool:
        """
        Input:
            1. key (str): Redis key for tracking failed login attempts.
            2. success (bool): Outcome of the attempted action.

        Process:
            1. Check if user is currently locked out.
            2. Reset failed attempts if action succeeded.
            3. Record failed attempt if action failed.
            4. Return final allowed status based on lockout and action outcome.

        Output:
            1. bool: True if action allowed, False if locked out.
        """
        # Step 1: Check if user is currently locked out
        if await LoginProtectionService.is_locked(key):
            return False  # Deny action if locked

        # Step 2: Reset failed attempts if action succeeded
        if success:
            await LoginProtectionService.reset_failed_attempts(key)

        else:
            # Step 3: Record a failed attempt if action failed
            await LoginProtectionService.record_failed_attempt(key)

        # Step 4: Return final allowed status based on lockout and action outcome
        return True


# ---------------------------- Service Instance ----------------------------
# Single global instance for login protection usage
login_protection_service = LoginProtectionService()
