# ---------------------------- External Imports ----------------------------
# Logging module for recording events, errors, and debugging information
import logging

# Module to capture and print detailed exception traces
import traceback

# FastAPI class for sending JSON responses to clients
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Service for JWT operations like token verification and decoding
from ..token_logic.jwt_service import jwt_service

# Service to handle password reset operations
from ..password_logic.password_reset_service import password_reset_service

# Service for login protection such as rate limiting and account lockouts
from ..security.login_protection_service import login_protection_service

# ---------------------------- Logger Setup ----------------------------
# Initialize a logger specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Password Reset Confirm Handler Class ----------------------------
# Class responsible for handling password reset confirmation logic
class PasswordResetConfirmHandler:

    # ---------------------------- Constructor ----------------------------
    # Initialize handler with required service dependencies
    def __init__(self):
        self.jwt_service = jwt_service
        self.password_reset_service = password_reset_service
        self.login_protection_service = login_protection_service

    # ---------------------------- Async Method to Handle Password Reset Confirmation ----------------------------
    # Confirm password reset and perform validation, logging, and brute-force checks
    async def handle_password_reset_confirm(self, token: str, new_password: str):

        try:
            # ---------------------------- Verify Token ----------------------------
            # Decode and validate the JWT token for password reset
            payload = await self.jwt_service.verify_token(token)
            
            # Return error if token is invalid or missing required email field
            if not payload or "email" not in payload:
                return JSONResponse({"error": "Invalid or expired token"}, status_code=400)

            # Extract user email from token payload
            email = payload["email"]
            
            # Key for tracking login attempts and potential lockouts
            email_lock_key = f"login_lock:email:{email}"

            # ---------------------------- Reset Password ----------------------------
            # Attempt to reset the user's password using the password reset service
            success = await self.password_reset_service.reset_password(token, new_password)
            
            # Determine response based on success of password reset
            if not success:
                status = 400
                content = {"error": "Invalid token or password"}
            else:
                status = 200
                content = {"message": "Password has been reset successfully"}

            # ---------------------------- Check Brute-force ----------------------------
            # Record this action and enforce lockout if too many failed attempts
            allowed = await self.login_protection_service.check_and_record_action(
                email_lock_key, success=(status == 200)
            )
            
            # Block further action if too many failed attempts occurred
            if not allowed:
                return JSONResponse({"error": "Too many failed attempts, temporarily locked"}, status_code=429)

            # Return the final JSON response
            return JSONResponse(content, status_code=status)

        except Exception:
            # Log any exceptions with full stack trace
            logger.error("Error during password reset confirm logic:\n%s", traceback.format_exc())
            
            # Return generic internal server error response
            return JSONResponse({"error": "Internal Server Error"}, status_code=500)


# ---------------------------- Instantiate Handler ----------------------------
# Create a single global instance of the handler for route usage
password_reset_confirm_handler = PasswordResetConfirmHandler()
