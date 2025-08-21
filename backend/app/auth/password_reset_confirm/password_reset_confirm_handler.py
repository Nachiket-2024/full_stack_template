# ---------------------------- External Imports ----------------------------
# For logging errors and capturing exception traces
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Core service for resetting passwords (handles token validation and password update)
from ..password_logic.password_reset_service import password_reset_service

# ---------------------------- Logger Setup ----------------------------
# Logger for this module to capture errors during password reset confirmation
logger = logging.getLogger(__name__)

# ---------------------------- Password Reset Confirm Handler Class ----------------------------
class PasswordResetConfirmHandler:
    """
    Handles the password reset confirmation step:
    - Validates the reset token
    - Updates the user's hashed password in the database
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self):
        # Assign the password reset service to an instance variable
        self.password_reset_service = password_reset_service

    # ---------------------------- Confirm Password Reset ----------------------------
    async def handle_password_reset_confirm(self, token: str, new_password: str):
        """
        Confirm a password reset request using the provided token.

        Parameters:
        - token: The password reset token sent to the user's email
        - new_password: The new password to set for the user

        Returns:
        - A dictionary with success or error message
        - HTTP status code
        """
        try:
            # ---------------------------- Reset Password ----------------------------
            # Call the core password reset service to update the user's password
            success = await self.password_reset_service.reset_password(token, new_password)

            # If the token is invalid or reset fails
            if not success:
                return {"error": "Invalid token or password"}, 400

            # Return success response
            return {"message": "Password has been reset successfully"}, 200

        except Exception:
            # Log the full traceback for debugging in case of unexpected errors
            logger.error("Error during password reset confirm logic:\n%s", traceback.format_exc())
            return {"error": "Internal Server Error"}, 500


# ---------------------------- Instantiate Handler ----------------------------
# Create a single instance to be used by routes
password_reset_confirm_handler = PasswordResetConfirmHandler()
