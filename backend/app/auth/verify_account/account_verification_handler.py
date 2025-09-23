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
            1. Decode and validate the verification token using account_verification_service.
            2. Check if token payload exists and contains "email".
            3. Extract the user email from payload.
            4. Generate a Redis key for tracking failed verification attempts.
            5. Attempt to mark the user as verified in the database via user_verification_service.
            6. Set response status and content based on whether verification succeeded.
            7. Record the action in login_protection_service and check for lockout.
            8. Return 429 if too many failed attempts occurred.
            9. Return final JSONResponse with success or error message.

        Output:
            1. JSONResponse: Success or error message with HTTP status code.
        """
        try:
            # Step 1: Decode and validate the verification token using account_verification_service
            payload = await self.account_verification_service.verify_token(token)

            # Step 2: Check if token payload exists and contains "email"
            if not payload or "email" not in payload:
                return JSONResponse(
                    content={"error": "Invalid, expired, or already used verification token"},
                    status_code=400
                )

            # Step 3: Extract the user email from payload
            email = payload["email"]

            # Step 4: Generate a Redis key for tracking failed verification attempts
            email_lock_key = f"login_lock:email:{email}"

            # Step 5: Attempt to mark the user as verified in the database via user_verification_service
            updated = await self.user_verification_service.mark_user_verified(email)

            # Step 6: Set response status and content based on whether verification succeeded
            status = 200 if updated else 400
            content = {"message": f"Account verified successfully for {email}."} if updated else {"error": "User not found or already verified"}

            # Step 7: Record the action in login_protection_service and check for lockout
            allowed = await self.login_protection_service.check_and_record_action(email_lock_key, success=(status == 200))

            # Step 8: Return 429 if too many failed attempts occurred
            if not allowed:
                return JSONResponse(
                    content={"error": "Too many failed attempts, account temporarily locked"},
                    status_code=429
                )

            # Step 9: Return final JSONResponse with success or error message
            return JSONResponse(content, status_code=status)

        except Exception:
            # Log exception with full stack trace
            logger.error("Error during account verification:\n%s", traceback.format_exc())

            # Return generic internal server error
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# ---------------------------- Singleton Instance ----------------------------
# Global instance for route usage
account_verification_handler = AccountVerificationHandler()
