# ---------------------------- External Imports ----------------------------
# Logging for tracking events, warnings, and errors
import logging

# Capture full stack traces for detailed exception debugging
import traceback

# FastAPI JSONResponse for sending structured HTTP responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Service to verify account tokens
from .account_verification_service import account_verification_service

# Service to mark users as verified
from .user_verification_service import user_verification_service

# Service for login protection (rate limiting, lockouts)
from ..security.login_protection_service import login_protection_service

# ---------------------------- Logger Setup ----------------------------
# Initialize a logger specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Account Verification Handler Class ----------------------------
# Class responsible for handling account verification requests
class AccountVerificationHandler:
    """
    1. handle_account_verification - Verify account using email token and enforce login protection.
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize handler with required service dependencies
    def __init__(self):
        # Service to decode and validate verification tokens
        self.account_verification_service = account_verification_service

        # Service to mark users as verified in database
        self.user_verification_service = user_verification_service

        # Service for brute-force protection during verification
        self.login_protection_service = login_protection_service

    # ---------------------------- Handle Account Verification ----------------------------
    async def handle_account_verification(self, token: str) -> JSONResponse:
        """
        Input:
            1. token (str): Verification token received via email.

        Process:
            1. Verify the token and decode payload.
            2. Extract user email from payload.
            3. Mark user as verified in the database.
            4. Record action with login protection and enforce lockout if necessary.

        Output:
            1. JSONResponse: Success or error message with HTTP status code.
        """
        try:
            # Decode and validate the verification token
            payload = await self.account_verification_service.verify_token(token)

            # Ensure payload exists and contains required email field
            if not payload or "email" not in payload:
                return JSONResponse(
                    content={"error": "Invalid, expired, or already used verification token"},
                    status_code=400
                )

            # Get user email from token payload
            email = payload["email"]

            # Key for tracking failed attempts per email
            email_lock_key = f"login_lock:email:{email}"

            # Update database record to mark user as verified
            updated = await self.user_verification_service.mark_user_verified(email)

            # Determine response content based on update outcome
            status = 200 if updated else 400
            content = {"message": f"Account verified successfully for {email}."} if updated else {"error": "User not found or already verified"}

            # Record the verification attempt and enforce lockout if necessary
            allowed = await self.login_protection_service.check_and_record_action(email_lock_key, success=(status == 200))

            # Deny further action if too many failed attempts
            if not allowed:
                return JSONResponse(
                    content={"error": "Too many failed attempts, account temporarily locked"},
                    status_code=429
                )
            
            # Return final success or error response
            return JSONResponse(content, status_code=status)

        except Exception:
            # Log exception with full stack trace
            logger.error("Error during account verification:\n%s", traceback.format_exc())

            # Return generic internal server error
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# ---------------------------- Singleton Instance ----------------------------
# Global instance for route usage
account_verification_handler = AccountVerificationHandler()
