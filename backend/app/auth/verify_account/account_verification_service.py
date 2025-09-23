# ---------------------------- External Imports ----------------------------
# Datetime utilities for timestamps and timezone-aware operations
from datetime import datetime, timedelta, timezone

# Logging module for tracking events and errors
import logging

# Capture full exception stack traces for debugging
import traceback

# JWT library for encoding and decoding tokens
import jwt

# For type hinting Celery tasks
from celery import Task

# ---------------------------- Internal Imports ----------------------------
# Application settings including SECRET_KEY, frontend URL, and token expirations
from ...core.settings import settings

# Celery task for sending emails asynchronously
from ...celery.email_tasks import send_email_task as _send_email_task

# Async Redis client for token storage and single-use verification
from ...redis.client import redis_client

# ---------------------------- Type Hint Celery Task ----------------------------
# This tells the IDE that send_email_task has Celery Task methods like apply_async
send_email_task: Task = _send_email_task

# ---------------------------- Logger Setup ----------------------------
# Configure module-specific logger
logger = logging.getLogger(__name__)

# ---------------------------- Account Verification Service Class ----------------------------
# Service for managing account verification emails and tokens
class AccountVerificationService:
    """
    1. send_verification_email - Generate a token, store in Redis, and send email via Celery.
    2. create_verification_token - Generate JWT token for account verification.
    3. verify_token - Validate verification token and enforce single-use.
    """

    # ---------------------------- Send Verification Email ----------------------------
    # Static method to send verification email asynchronously via Celery
    @staticmethod
    async def send_verification_email(email: str, table: str, expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES) -> bool:
        """
        Input:
            1. email (str): Recipient's email address.
            2. table (str): Role table for user.
            3. expires_minutes (int): Token expiration in minutes.

        Process:
            1. Generate verification token for user with expiration.
            2. Store token in Redis with expiration to enforce single-use.
            3. Build frontend verification URL with token.
            4. Schedule asynchronous email task via Celery.
            5. Return true if email scheduled successfully

        Output:
            1. bool: True if email scheduled successfully, False otherwise.
        """
        try:
            # Step 1: Generate verification token for user with expiration
            verification_token = await AccountVerificationService.create_verification_token(email, table, expires_minutes)

            # Step 2: Store token in Redis with expiration to enforce single-use
            await redis_client.set(f"verify:{verification_token}", "1", ex=expires_minutes * 60)

            # Step 3: Build frontend verification URL with token
            verify_url = f"{settings.FRONTEND_BASE_URL}/verify-account?token={verification_token}"

            # Step 4: Schedule asynchronous email task via Celery
            send_email_task.apply_async(
                kwargs={
                    "to_email": email,
                    "subject": "Account Verification",
                    "body": f"Click the link to verify your account: {verify_url}"
                }
            )

            # Log success
            logger.info("Verification email scheduled for %s", email)

            # Step 5: Return true if email scheduled successfully
            return True

        except Exception:
            # Log unexpected errors
            logger.error("Error sending verification email:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Create Verification Token ----------------------------
    @staticmethod
    async def create_verification_token(email: str, table: str, expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES) -> str:
        """
        Input:
            1. email (str): User email.
            2. table (str): Role table for the user.
            3. expires_minutes (int): Expiration time in minutes.

        Process:
            1. Compute expiration datetime in UTC.
            2. Build JWT payload including email, table, and expiration.
            3. Encode payload into JWT token.

        Output:
            1. str: Encoded JWT verification token.
        """
        # Step 1: Compute expiration datetime in UTC
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

        # Step 2: Build JWT payload including email, table, and expiration
        payload: dict[str, str | float] = {
            "email": email,
            "table": table,
            "exp": expire.timestamp()
        }

        # Step 3: Encode payload into JWT token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        return token

    # ---------------------------- Verify Token ----------------------------
    @staticmethod
    async def verify_token(token: str) -> dict | None:
        """
        Input:
            1. token (str): Verification token to validate.

        Process:
            1. Decode JWT token using secret key and algorithm.
            2. Check Redis for single-use enforcement.
            3. Delete token from Redis to prevent reuse.
            4. Return decoded payload

        Output:
            1. dict | None: Decoded payload if valid, else None.
        """
        try:
            # Step 1: Decode JWT token using secret key and algorithm
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

            # Step 2: Check Redis for single-use enforcement
            exists = await redis_client.get(f"verify:{token}")
            if not exists:
                # Token not found or already used
                logger.warning("Verification token not found or already used")
                return None

            # Step 3: Delete token from Redis to prevent reuse
            await redis_client.delete(f"verify:{token}")

            # Step 4: Return decoded payload
            return payload

        except jwt.ExpiredSignatureError:
            # Expired token
            logger.warning("Expired verification token used")
            return None

        except jwt.InvalidTokenError:
            # Invalid token
            logger.warning("Invalid verification token used")
            return None

        except Exception:
            # Unexpected errors
            logger.error("Error verifying account verification token:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
# Singleton instance for account verification operations
account_verification_service = AccountVerificationService()
