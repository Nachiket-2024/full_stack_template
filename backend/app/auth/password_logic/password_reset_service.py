# ---------------------------- External Imports ----------------------------
# Logging module for tracking events and warnings/errors
import logging

# Traceback module to capture detailed exception stack traces
import traceback

# Celery Task class for type hinting asynchronous tasks
from celery import Task

# ---------------------------- Internal Imports ----------------------------
# Password service for creating and verifying tokens, hashing passwords
from .password_service import password_service

# Celery task for sending emails asynchronously
from ...celery.email_tasks import send_email_task as _send_email_task

# Role tables and default role configuration for user management
from ...access_control.role_tables import ROLE_TABLES, DEFAULT_ROLE

# Settings module for frontend URLs and app configuration
from ...core.settings import settings

# ---------------------------- Type Hint Celery Task ----------------------------
# Assign the imported Celery task to a typed variable for IDE support
send_email_task: Task = _send_email_task

# ---------------------------- Logger Setup ----------------------------
# Initialize a logger specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Password Reset Service ----------------------------
# Service class handling password reset requests and updates
class PasswordResetService:

    # ---------------------------- Send Reset Email ----------------------------
    # Static method to send a password reset email for a given user and role
    @staticmethod
    async def send_reset_email(email: str, role: str | None = None) -> bool:

        try:
            # Use default role if none is provided
            if role is None:
                role = DEFAULT_ROLE

            # Check if the provided role exists in role tables
            if role not in ROLE_TABLES:
                logger.warning("Attempt to send reset email for invalid role: %s", role)
                return False

            # Generate a short-lived password reset token for the email
            reset_token = await password_service.create_reset_token(email, role)

            # Construct the frontend URL for password reset
            reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password?token={reset_token}"

            # Schedule sending the reset email asynchronously using Celery
            send_email_task.apply_async(
                kwargs={
                    "to_email": email,
                    "subject": "Password Reset Request",
                    "body": f"Click the link to reset your password: {reset_url}"
                }
            )

            # Log that the reset email has been scheduled successfully
            logger.info("Password reset email scheduled for %s for role %s", email, role)
            return True

        except Exception:
            # Log any exceptions that occur during email sending
            logger.error("Error sending reset email:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Reset Password ----------------------------
    # Static method to validate a token and update the user's password
    @staticmethod
    async def reset_password(token: str, new_password: str) -> bool:

        try:
            # Verify the reset token and retrieve its payload
            payload = await password_service.verify_reset_token(token)
            if not payload:
                logger.warning("Invalid or expired password reset token.")
                return False

            # Extract user email and role from token, fallback to default role
            email = payload.get("email")
            role = payload.get("role", DEFAULT_ROLE)

            # Validate that the role exists in role tables
            if role not in ROLE_TABLES:
                logger.warning("Invalid role from reset token: %s", role)
                return False

            # Check if the new password meets strength requirements
            if not await password_service.validate_password_strength(new_password):
                logger.warning("Weak password provided during reset for email: %s", email)
                return False

            # Hash the new password before saving
            hashed_password = await password_service.hash_password(new_password)

            # Update the hashed password in the database for the specified role
            updated = await ROLE_TABLES[role].update_by_email(email, {"hashed_password": hashed_password})
            if updated:
                logger.info("Password reset successful for email: %s in role %s", email, role)
                return True

            return False

        except Exception:
            # Log any exceptions encountered during password reset
            logger.error("Error during password reset:\n%s", traceback.format_exc())
            return False


# ---------------------------- Service Instance ----------------------------
# Single shared instance of the password reset service
password_reset_service = PasswordResetService()
