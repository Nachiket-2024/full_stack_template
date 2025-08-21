# ---------------------------- External Imports ----------------------------
from datetime import datetime, timedelta, timezone
import logging
import traceback
import jwt

# For type hinting Celery tasks
from celery import Task

# ---------------------------- Internal Imports ----------------------------
from ...core.settings import settings
from ...celery.email_tasks import send_email_task as _send_email_task
from ...redis.client import redis_client

# ---------------------------- Type Hint Celery Task ----------------------------
# This tells the IDE that send_email_task has Celery Task methods like apply_async
send_email_task: Task = _send_email_task

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)

# ---------------------------- Account Verification Service ----------------------------
class AccountVerificationService:
    """
    Service to handle account email verification:
    - Generate verification token
    - Send verification email asynchronously
    - Store token in Redis for single-use
    - Verify token and mark account as verified
    """

    # ---------------------------- Send Verification Email ----------------------------
    @staticmethod
    async def send_verification_email(email: str, 
                                      table: str, 
                                      expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES
                                      ) -> bool:
        """
        Generate an account verification token, store in Redis, and send email via Celery.
        """
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

            logger.info("Verification email scheduled for %s", email)
            return True

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
        Generate a JWT token for account verification (default 24 hours expiry).
        """
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        payload: dict[str, str | float] = {
            "email": email,
            "table": table,
            "exp": expire.timestamp()
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token

    # ---------------------------- Verify Token ----------------------------
    @staticmethod
    async def verify_token(token: str) -> dict | None:
        """
        Verify account verification token:
        - Check JWT signature & expiry
        - Check token exists in Redis (single-use)
        - Delete token after successful verification
        """
        try:
            # Decode JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

            # Check Redis for single-use
            exists = await redis_client.get(f"verify:{token}")
            if not exists:
                logger.warning("Verification token not found or already used")
                return None

            # Delete token to prevent reuse
            await redis_client.delete(f"verify:{token}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Expired verification token used")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid verification token used")
            return None
        except Exception:
            logger.error("Error verifying account verification token:\n%s", traceback.format_exc())
            return None

# ---------------------------- Service Instance ----------------------------
account_verification_service = AccountVerificationService()
