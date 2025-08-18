# ---------------------------- External Imports ----------------------------
# For logging and traceback
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Password service for hashing new password
from .password_service import password_service

# JWT service for reset token
from .jwt_service import jwt_service

# Celery task to send email asynchronously
from ...celery.email_tasks import send_email_task

# ---------------------------- Logger Setup ----------------------------
# Configure logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Password Reset Service ----------------------------
class PasswordResetService:
    """
    Service to handle password reset process:
    - Generate reset token
    - Send reset email asynchronously
    - Verify token and reset password
    """

    # ---------------------------- Send Reset Email ----------------------------
    @staticmethod
    async def send_reset_email(email: str, table_name: str) -> bool:
        """
        Generate a password reset token and send email via Celery.
        """
        try:
            # Create short-lived reset token (default 15 mins)
            reset_token = await password_service.create_reset_token(email, table_name)

            # Compose reset URL (frontend endpoint)
            reset_url = f"https://yourfrontend.com/reset-password?token={reset_token}"

            # Send email asynchronously using Celery
            await send_email_task.delay(
                to_email=email,
                subject="Password Reset Request",
                body=f"Click the link to reset your password: {reset_url}"
            )
            logger.info("Password reset email sent to %s", email)
            return True

        except Exception:
            logger.error("Error sending reset email:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Reset Password ----------------------------
    @staticmethod
    async def reset_password(token: str, new_password: str, crud_instance) -> bool:
        """
        Verify the token and update password for the user.
        Requires the correct CRUD instance for the role table.
        """
        try:
            # Decode and verify token
            payload = await password_service.verify_reset_token(token)
            if not payload:
                logger.warning("Invalid or expired password reset token.")
                return False

            email = payload.get("sub")
            table_name = payload.get("table")

            # Validate password strength
            if not await password_service.validate_password_strength(new_password):
                logger.warning("Weak password provided during reset for email: %s", email)
                return False

            # Hash new password
            hashed_password = await password_service.hash_password(new_password)

            # Update password in DB
            updated = await crud_instance.update_by_email(email, {"hashed_password": hashed_password})
            if updated:
                logger.info("Password reset successful for email: %s", email)
                return True
            return False

        except Exception:
            logger.error("Error during password reset:\n%s", traceback.format_exc())
            return False

# ---------------------------- Service Instance ----------------------------
# Single instance for global use
password_reset_service = PasswordResetService()
