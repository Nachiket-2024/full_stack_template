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
    @staticmethod
    async def send_verification_email(email: str, 
                                      table: str, 
                                      expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES
                                      ) -> bool:
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
            # ---------------------------- Generate Token ----------------------------
            verification_token = await AccountVerificationService.create_verification_token(
                email, table, expires_minutes
            )

            # ---------------------------- Store Token in Redis ----------------------------
            await redis_client.set(f"verify:{verification_token}", "1", ex=expires_minutes * 60)

            # ---------------------------- Build Verification URL ----------------------------
            verify_url = f"{settings.FRONTEND_BASE_URL}/verify-account?token={verification_token}"

            # ---------------------------- Schedule Celery Email Task ----------------------------
            send_email_task.apply_async(
                kwargs={
                    "to_email": email,
                    "subject": "Account Verification",
                    "body": f"Click the link to verify your account: {verify_url}"
                }
            )

            # ---------------------------- Log Success ----------------------------
            logger.info("Verification email scheduled for %s", email)
            return True

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            logger.error("Error sending verification email:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Create Verification Token ----------------------------
    @staticmethod
    async def create_verification_token(email: str, 
                                        table: str, 
                                        expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES
                                        ) -> str:
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
        # ---------------------------- Compute Expiration ----------------------------
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

        # ---------------------------- Build JWT Payload ----------------------------
        payload: dict[str, str | float] = {
            "email": email,
            "table": table,
            "exp": expire.timestamp()
        }

        # ---------------------------- Encode JWT ----------------------------
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token

    # ---------------------------- Verify Token ----------------------------
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
            # ---------------------------- Decode JWT ----------------------------
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

            # ---------------------------- Check Single-use in Redis ----------------------------
            exists = await redis_client.get(f"verify:{token}")
            if not exists:
                logger.warning("Verification token not found or already used")
                return None

            # ---------------------------- Delete Token to Enforce Single-use ----------------------------
            await redis_client.delete(f"verify:{token}")
            return payload

        # ---------------------------- Token Expired ----------------------------
        except jwt.ExpiredSignatureError:
            logger.warning("Expired verification token used")
            return None

        # ---------------------------- Token Invalid ----------------------------
        except jwt.InvalidTokenError:
            logger.warning("Invalid verification token used")
            return None

        # ---------------------------- Unexpected Exception ----------------------------
        except Exception:
            logger.error("Error verifying account verification token:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
# Singleton instance for account verification operations
account_verification_service = AccountVerificationService()
