# ---------------------------- External Imports ----------------------------
# Logging for tracking events and debugging
import logging
import traceback

# FastAPI response class for sending JSON responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Core password reset service for sending tokens
from ..password_logic.password_reset_service import password_reset_service

# Role tables to find users in different roles
from ...access_control.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- Password Reset Request Handler Class ----------------------------
# Class responsible for handling password reset request flow
class PasswordResetRequestHandler:
    """
    Handles password reset requests:
    - Sends reset token via email if the user exists
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize handler with required services and role tables
    def __init__(self):
        self.password_reset_service = password_reset_service
        self.role_tables = ROLE_TABLES

    # ---------------------------- Request Password Reset ----------------------------
    # Process password reset request and send token if user exists
    async def handle_password_reset_request(self, email: str):
        """
        Process password reset request and return JSONResponse.

        Parameters:
        - email: Email of the user requesting reset

        Returns:
        - JSONResponse with generic success message
        """
        try:
            # Flag to track if a user is found
            user_found = False
            
            # Search for user in all role tables
            for role, crud in self.role_tables.items():
                user = await crud.get_by_email(email)
                
                # If user exists, send reset email and stop searching
                if user:
                    user_found = True
                    await self.password_reset_service.send_reset_email(email, role)
                    break

            # Log request for non-existing emails without revealing info
            if not user_found:
                logger.info("Password reset requested for non-existing email: %s", email)

            # Return generic success response regardless of user existence
            return JSONResponse(
                content={"message": "If the email exists, a reset link has been sent."},
                status_code=200
            )

        except Exception:
            # Log the error with stack trace
            logger.error("Error during password reset request logic:\n%s", traceback.format_exc())
            # Return generic server error response
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)

# ---------------------------- Instantiate PasswordResetRequestHandler ----------------------------
# Singleton instance for route usage
password_reset_request_handler = PasswordResetRequestHandler()
