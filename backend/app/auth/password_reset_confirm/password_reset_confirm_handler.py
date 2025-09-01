# ---------------------------- External Imports ----------------------------
# For logging events, errors, and debugging information
import logging

# For printing detailed exception traces in case of errors
import traceback

# FastAPI response class for sending JSON responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Service for handling JWT token operations
from ..token_logic.jwt_service import jwt_service

# Service for handling password reset logic
from ..password_logic.password_reset_service import password_reset_service

# Service for login protection like rate limiting and lockouts
from ..security.login_protection_service import login_protection_service

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- Password Reset Confirm Handler Class ----------------------------
# Class responsible for handling password reset confirmation flow
class PasswordResetConfirmHandler:
    """
    Handles the entire password reset confirmation flow:
    - Verifies token
    - Updates password
    - Applies brute-force protection
    - Returns JSONResponse
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize handler with required services
    def __init__(self):
        self.jwt_service = jwt_service
        self.password_reset_service = password_reset_service
        self.login_protection_service = login_protection_service

    # ---------------------------- Async Method to Handle Password Reset Confirmation ----------------------------
    # Confirm password reset and perform all necessary checks
    async def handle_password_reset_confirm(self, token: str, new_password: str):
        """
        Confirm password reset and handle all checks internally.

        Parameters:
        - token: JWT password reset token
        - new_password: New password to set

        Returns:
        - JSONResponse
        """
        try:
            # ---------------------------- Verify Token ----------------------------
            # Decode and validate the password reset JWT token
            payload = await self.jwt_service.verify_token(token)
            
            # Check if token is valid and contains email
            if not payload or "email" not in payload:
                return JSONResponse({"error": "Invalid or expired token"}, status_code=400)

            # Extract email from token payload
            email = payload["email"]
            
            # Unique key for tracking login/account actions
            email_lock_key = f"login_lock:email:{email}"

            # ---------------------------- Reset Password ----------------------------
            # Attempt to reset the password using the password reset service
            success = await self.password_reset_service.reset_password(token, new_password)
            
            # Determine response status and message based on reset success
            if not success:
                status = 400
                content = {"error": "Invalid token or password"}
            else:
                status = 200
                content = {"message": "Password has been reset successfully"}

            # ---------------------------- Check Brute-force ----------------------------
            # Record the reset attempt and enforce lockout if necessary
            allowed = await self.login_protection_service.check_and_record_action(email_lock_key, success=(status==200))
            
            # If too many failed attempts, block further action
            if not allowed:
                return JSONResponse({"error": "Too many failed attempts, temporarily locked"}, status_code=429)

            # Return the final response
            return JSONResponse(content, status_code=status)

        except Exception:
            # Log the error with stack trace
            logger.error("Error during password reset confirm logic:\n%s", traceback.format_exc())
            # Return generic server error response
            return JSONResponse({"error": "Internal Server Error"}, status_code=500)

# ---------------------------- Instantiate Handler ----------------------------
# Create a global instance of PasswordResetConfirmHandler for usage in routes
password_reset_confirm_handler = PasswordResetConfirmHandler()
