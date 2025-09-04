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
    """
    1. send_reset_email - Generate reset token, send password reset email via Celery.
    2. reset_password - Validate token, hash new password, and update user in DB.
    """

    # ---------------------------- Send Reset Email ----------------------------
    # Static method to send a password reset email for a given user and role
    @staticmethod
    async def send_reset_email(email: str, role: str | None = None) -> bool:
        """
        Input:
            1. email (str): Email of the user requesting password reset.
            2. role (str | None): Role of the user; uses default role if None.

        Process:
            1. Determine user role; fallback to default if not provided.
            2. Validate that role exists in ROLE_TABLES.
            3. Generate password reset token via password_service.
            4. Construct frontend reset URL with token.
            5. Schedule email sending asynchronously via Celery task.

        Output:
            1. bool: True if email scheduled successfully, False otherwise.
        """
        try:
            # ---------------------------- Default Role ----------------------------
            # Use default role if none provided
            if role is None:
                role = DEFAULT_ROLE

            # ---------------------------- Role Validation ----------------------------
            # Ensure role exists in ROLE_TABLES
            if role not in ROLE_TABLES:
                logger.warning("Attempt to send reset email for invalid role: %s", role)
                return False

            # ---------------------------- Generate Reset Token ----------------------------
            # Create short-lived password reset token
            reset_token = await password_service.create_reset_token(email, role)

            # ---------------------------- Construct Reset URL ----------------------------
            # Frontend link for password reset page
            reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password?token={reset_token}"

            # ---------------------------- Schedule Email ----------------------------
            # Send email asynchronously using Celery task
            send_email_task.apply_async(
                kwargs={
                    "to_email": email,
                    "subject": "Password Reset Request",
                    "body": f"Click the link to reset your password: {reset_url}"
                }
            )

            # ---------------------------- Log Success ----------------------------
            # Log successful scheduling of password reset email
            logger.info("Password reset email scheduled for %s for role %s", email, role)
            return True

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log any errors encountered during email scheduling
            logger.error("Error sending reset email:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Reset Password ----------------------------
    # Static method to validate a token and update the user's password
    @staticmethod
    async def reset_password(token: str, new_password: str) -> bool:
        """
        Input:
            1. token (str): Password reset token from user.
            2. new_password (str): New password provided by user.

        Process:
            1. Verify reset token via password_service.
            2. Extract email and role from token payload.
            3. Validate role exists in ROLE_TABLES.
            4. Check password strength.
            5. Hash the new password.
            6. Update user's hashed password in database.

        Output:
            1. bool: True if password reset successfully, False otherwise.
        """
        try:
            # ---------------------------- Verify Token ----------------------------
            # Validate reset token and extract payload
            payload = await password_service.verify_reset_token(token)
            if not payload:
                logger.warning("Invalid or expired password reset token.")
                return False

            # ---------------------------- Extract User Info ----------------------------
            # Get email and role from token; fallback to default role
            email = payload.get("email")
            role = payload.get("role", DEFAULT_ROLE)

            # ---------------------------- Role Validation ----------------------------
            # Ensure role exists in ROLE_TABLES
            if role not in ROLE_TABLES:
                logger.warning("Invalid role from reset token: %s", role)
                return False

            # ---------------------------- Validate Password Strength ----------------------------
            # Ensure new password meets complexity requirements
            if not await password_service.validate_password_strength(new_password):
                logger.warning("Weak password provided during reset for email: %s", email)
                return False

            # ---------------------------- Hash Password ----------------------------
            # Securely hash the new password
            hashed_password = await password_service.hash_password(new_password)

            # ---------------------------- Update Database ----------------------------
            # Update user's hashed password in database
            updated = await ROLE_TABLES[role].update_by_email(email, {"hashed_password": hashed_password})
            if updated:
                logger.info("Password reset successful for email: %s in role %s", email, role)
                return True

            return False

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log errors encountered during password reset process
            logger.error("Error during password reset:\n%s", traceback.format_exc())
            return False


# ---------------------------- Service Instance ----------------------------
# Single shared instance of the password reset service
password_reset_service = PasswordResetService()
