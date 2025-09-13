# ---------------------------- External Imports ----------------------------
# Datetime utilities for timestamps and timezone-aware operations
from datetime import datetime, timedelta, timezone

# Logging module for tracking events and errors
import logging

# Capture full exception stack traces
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
            1. Generate verification token with expiration.
            2. Store token in Redis for single-use tracking.
            3. Compose verification URL with token.
            4. Schedule asynchronous email task via Celery.

        Output:
            1. bool: True if email scheduled successfully, False on failure.
        """
        try:
            # Generate verification token for user
            verification_token = await AccountVerificationService.create_verification_token(email, table, expires_minutes)

            # Store token in Redis with expiration for single-use enforcement
            await redis_client.set(f"verify:{verification_token}", "1", ex=expires_minutes * 60)

            # Construct frontend verification URL including token
            verify_url = f"{settings.FRONTEND_BASE_URL}/verify-account?token={verification_token}"

            # Schedule asynchronous email task via Celery
            send_email_task.apply_async(
                kwargs={
                    # Recipient email
                    "to_email": email,

                    # Email subject
                    "subject": "Account Verification",

                    # Email body with verification link
                    "body": f"Click the link to verify your account: {verify_url}"
                }
            )

            # Log successful scheduling of email
            logger.info("Verification email scheduled for %s", email)

            # Return True indicating success
            return True

        # Catch unexpected exceptions during email sending
        except Exception:
            # Log full traceback for debugging
            logger.error("Error sending verification email:\n%s", traceback.format_exc())

            # Return False indicating failure
            return False

    # ---------------------------- Create Verification Token ----------------------------
    # Static method to create JWT verification token
    @staticmethod
    async def create_verification_token(email: str, table: str, expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES) -> str:
        """
        Input:
            1. email (str): User email.
            2. table (str): Role table for the user.
            3. expires_minutes (int): Expiration time in minutes.

        Process:
            1. Compute expiration datetime.
            2. Build JWT payload including email, table, and expiration.
            3. Encode JWT token.

        Output:
            1. str: JWT verification token.
        """
        # Calculate expiration datetime in UTC
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

        # Create payload dictionary for JWT token
        payload: dict[str, str | float] = {
            "email": email,  # User email
            "table": table,  # User role table
            "exp": expire.timestamp()  # Expiration timestamp
        }

        # Encode payload into JWT token using secret and algorithm
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        # Return encoded token
        return token

    # ---------------------------- Verify Token ----------------------------
    # Static method to verify JWT token and enforce single-use
    @staticmethod
    async def verify_token(token: str) -> dict | None:
        """
        Input:
            1. token (str): Verification token to validate.

        Process:
            1. Decode JWT token.
            2. Check Redis for single-use enforcement.
            3. Delete token from Redis to prevent reuse.

        Output:
            1. dict | None: Decoded payload if valid, else None.
        """
        try:
            # Decode token using secret key and algorithm
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

            # Check if token exists in Redis
            exists = await redis_client.get(f"verify:{token}")
            
            # Return None if token not found or already used
            if not exists:
                logger.warning("Verification token not found or already used")
                return None

            # Delete token from Redis to prevent reuse
            await redis_client.delete(f"verify:{token}")

            # Return decoded payload
            return payload

        except jwt.ExpiredSignatureError:
            # Log expired token usage
            logger.warning("Expired verification token used")
            return None

        except jwt.InvalidTokenError:
            # Log invalid token usage
            logger.warning("Invalid verification token used")
            return None

        except Exception:
            # Log unexpected errors with traceback
            logger.error("Error verifying account verification token:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
# Singleton instance for account verification operations
account_verification_service = AccountVerificationService()
