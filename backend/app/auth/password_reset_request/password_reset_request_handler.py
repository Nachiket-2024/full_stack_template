# ---------------------------- External Imports ----------------------------
# For logging and handling exceptions
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Import the core password reset service
from ..password_logic.password_reset_service import password_reset_service

# Role tables to find users
from ...core.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Logger for this module
logger = logging.getLogger(__name__)

# ---------------------------- Password Reset Handler Class ----------------------------
class PasswordResetRequestHandler:
    """
    Handles the password reset flow:
    1. Requesting a password reset (sends reset token via email)
    2. Confirming password reset (updates user's password)
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self):
        # Assign internal services to instance variables
        self.password_reset_service = password_reset_service
        self.role_tables = ROLE_TABLES

    # ---------------------------- Request Password Reset ----------------------------
    async def handle_password_reset_request(self, email: str):
        """
        Handle password reset request.
        Sends reset token via email if user exists.
        """
        try:
            # Find user and send reset token
            user_found = False
            for role, crud in self.role_tables.items():
                user = await crud.get_by_email(email)
                if user:
                    user_found = True
                    await self.password_reset_service.send_reset_email(email, role)
                    break

            # Log request for non-existing emails without revealing info
            if not user_found:
                logger.info("Password reset requested for non-existing email: %s", email)

            # Generic success response
            return {"message": "If the email exists, a reset link has been sent."}, 200

        except Exception:
            # Log unexpected errors
            logger.error("Error during password reset request logic:\n%s", traceback.format_exc())
            return {"error": "Internal Server Error"}, 500

    # ---------------------------- Confirm Password Reset ----------------------------
    async def handle_password_reset_confirm(self, token: str, new_password: str):
        """
        Confirm password reset using token.
        Updates user's hashed password in the database.
        """
        try:
            # Reset password via core service
            success = await self.password_reset_service.reset_password(token, new_password)
            if not success:
                return {"error": "Invalid token or password"}, 400

            # Success response
            return {"message": "Password has been reset successfully"}, 200

        except Exception:
            # Log unexpected errors
            logger.error("Error during password reset confirm logic:\n%s", traceback.format_exc())
            return {"error": "Internal Server Error"}, 500


# ---------------------------- Instantiate PasswordResetHandler ----------------------------
password_reset_request_handler = PasswordResetRequestHandler()
