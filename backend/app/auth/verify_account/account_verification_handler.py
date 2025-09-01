# ---------------------------- External Imports ----------------------------
# For logging events, errors, and debugging information
import logging

# For printing detailed exception traces in case of errors
import traceback

# FastAPI response class for sending JSON responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Service for verifying account tokens
from .account_verification_service import account_verification_service

# Service for marking users as verified
from .user_verification_service import user_verification_service

# Service for login protection like rate limiting and lockouts
from ..security.login_protection_service import login_protection_service

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- Account Verification Handler Class ----------------------------
# Class responsible for handling account verification requests
class AccountVerificationHandler:
    """
    Handles user account verification via email tokens:
    - Validates token
    - Marks user as verified
    - Applies brute-force protection
    - Returns JSONResponse
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize the handler with required services
    def __init__(self):
        self.account_verification_service = account_verification_service
        self.user_verification_service = user_verification_service
        self.login_protection_service = login_protection_service

    # ---------------------------- Async Method to Handle Verification ----------------------------
    # Verify account using email token
    async def handle_account_verification(self, token: str):
        """
        Verify account using token and return JSONResponse.

        Parameters:
        - token: JWT token sent to user's email

        Returns:
        - JSONResponse
        """
        try:
            # ---------------------------- Verify Token ----------------------------
            # Decode and validate the token
            payload = await self.account_verification_service.verify_token(token)
            
            # Check if payload is valid and contains email
            if not payload or "email" not in payload:
                return JSONResponse({"error": "Invalid, expired, or already used verification token"}, status_code=400)

            # Extract email from token payload
            email = payload["email"]
            
            # Unique key for tracking login/account actions
            email_lock_key = f"login_lock:email:{email}"

            # ---------------------------- Mark User Verified ----------------------------
            # Mark the user as verified in the database
            updated = await self.user_verification_service.mark_user_verified(email)
            
            # Determine response status and message
            status = 200 if updated else 400
            content = {"message": f"Account verified successfully for {email}."} if updated else {"error": "User not found or already verified"}

            # ---------------------------- Brute-force Protection ----------------------------
            # Record the verification attempt and enforce lockout if necessary
            allowed = await self.login_protection_service.check_and_record_action(email_lock_key, success=(status==200))
            
            # If too many failed attempts, block further verification
            if not allowed:
                return JSONResponse({"error": "Too many failed attempts, account temporarily locked"}, status_code=429)

            # Return the final response
            return JSONResponse(content, status_code=status)

        except Exception:
            # Log the error with stack trace
            logger.error("Error during account verification:\n%s", traceback.format_exc())
            # Return generic server error response
            return JSONResponse({"error": "Internal Server Error"}, status_code=500)

# ---------------------------- Instantiate Handler ----------------------------
# Create a global instance of AccountVerificationHandler for usage in routes
account_verification_handler = AccountVerificationHandler()
