# ---------------------------- External Imports ----------------------------
# For logging and handling exceptions
import logging
import traceback

# For type hinting Celery tasks
from celery import Task

# ---------------------------- Internal Imports ----------------------------
# Password service to create/verify tokens and hash passwords
from .password_service import password_service

# Celery task to send emails asynchronously
from ...celery.email_tasks import send_email_task as _send_email_task

# Role tables and default role for user management
from ...access_control.role_tables import ROLE_TABLES, DEFAULT_ROLE

# Settings for frontend URLs
from ...core.settings import settings

# ---------------------------- Type Hint Celery Task ----------------------------
# Tells IDE that send_email_task behaves like a Celery Task
send_email_task: Task = _send_email_task

# ---------------------------- Logger Setup ----------------------------
# Create a logger for this module
logger = logging.getLogger(__name__)

# ---------------------------- Password Reset Service ----------------------------
class PasswordResetService:
    """
    Core service to handle password reset logic:
    - Generate reset token
    - Send reset email via Celery
    - Verify token and reset password
    """

    # ---------------------------- Send Reset Email ----------------------------
    @staticmethod
    async def send_reset_email(email: str, role: str | None = None) -> bool:
        """
        Generate a password reset token and send email via Celery.
        Returns True if email task scheduled successfully.
        """
        try:
            # Use default role if none provided
            if role is None:
                role = DEFAULT_ROLE

            # Ensure role exists in ROLE_TABLES
            if role not in ROLE_TABLES:
                logger.warning("Attempt to send reset email for invalid role: %s", role)
                return False

            # Create a short-lived reset token for the user
            reset_token = await password_service.create_reset_token(email, role)

            # Build the frontend reset URL
            reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password?token={reset_token}"

            # Schedule email via Celery task
            send_email_task.apply_async(
                kwargs={
                    "to_email": email,
                    "subject": "Password Reset Request",
                    "body": f"Click the link to reset your password: {reset_url}"
                }
            )

            # Log success
            logger.info("Password reset email scheduled for %s for role %s", email, role)
            return True

        except Exception:
            # Log any exception that occurs
            logger.error("Error sending reset email:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Reset Password ----------------------------
    @staticmethod
    async def reset_password(token: str, new_password: str) -> bool:
        """
        Verify the token and update password for the user.
        Returns True if password update successful.
        """
        try:
            # Decode and verify the reset token
            payload = await password_service.verify_reset_token(token)
            if not payload:
                logger.warning("Invalid or expired password reset token.")
                return False

            # Extract email and role from token payload
            email = payload.get("email")
            role = payload.get("role", DEFAULT_ROLE)

            # Ensure role exists in ROLE_TABLES
            if role not in ROLE_TABLES:
                logger.warning("Invalid role from reset token: %s", role)
                return False

            # Validate password strength
            if not await password_service.validate_password_strength(new_password):
                logger.warning("Weak password provided during reset for email: %s", email)
                return False

            # Hash the new password
            hashed_password = await password_service.hash_password(new_password)

            # Update password in the database
            updated = await ROLE_TABLES[role].update_by_email(email, {"hashed_password": hashed_password})
            if updated:
                logger.info("Password reset successful for email: %s in role %s", email, role)
                return True

            return False

        except Exception:
            # Log any exception during password reset
            logger.error("Error during password reset:\n%s", traceback.format_exc())
            return False


# ---------------------------- Service Instance ----------------------------
# Single instance of the service for use in other modules
password_reset_service = PasswordResetService()
