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

# ---------------------------- Account Verification Service ----------------------------
# Service for managing account verification emails and tokens
class AccountVerificationService:

    # ---------------------------- Send Verification Email ----------------------------
    @staticmethod
    async def send_verification_email(email: str, 
                                      table: str, 
                                      expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES
                                      ) -> bool:

        try:
            # Create short-lived verification token
            verification_token = await AccountVerificationService.create_verification_token(
                email, table, expires_minutes
            )

            # Store token in Redis with expiry
            await redis_client.set(f"verify:{verification_token}", "1", ex=expires_minutes * 60)

            # Compose verification URL (frontend endpoint)
            verify_url = f"{settings.FRONTEND_BASE_URL}/verify-account?token={verification_token}"

            # Schedule Celery task (IDE will recognize apply_async)
            send_email_task.apply_async(
                kwargs={
                    "to_email": email,
                    "subject": "Account Verification",
                    "body": f"Click the link to verify your account: {verify_url}"
                }
            )

            # Log that email scheduling succeeded
            logger.info("Verification email scheduled for %s", email)
            return True

        except Exception:
            # Log full stack trace on failure
            logger.error("Error sending verification email:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Create Verification Token ----------------------------
    @staticmethod
    async def create_verification_token(email: str, 
                                        table: str, 
                                        expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES
                                        ) -> str:

        # Compute expiration datetime
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        # Build JWT payload
        payload: dict[str, str | float] = {
            "email": email,
            "table": table,
            "exp": expire.timestamp()
        }
        # Encode payload into JWT token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token

    # ---------------------------- Verify Token ----------------------------
    @staticmethod
    async def verify_token(token: str) -> dict | None:

        try:
            # Decode JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

            # Check Redis for single-use token
            exists = await redis_client.get(f"verify:{token}")
            if not exists:
                logger.warning("Verification token not found or already used")
                return None

            # Delete token from Redis to prevent reuse
            await redis_client.delete(f"verify:{token}")
            return payload

        except jwt.ExpiredSignatureError:
            # Token has expired
            logger.warning("Expired verification token used")
            return None
        
        except jwt.InvalidTokenError:
            # Token is invalid
            logger.warning("Invalid verification token used")
            return None
        
        except Exception:
            # Log any unexpected error
            logger.error("Error verifying account verification token:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
# Singleton instance for account verification operations
account_verification_service = AccountVerificationService()
