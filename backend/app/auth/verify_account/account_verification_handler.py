# ---------------------------- External Imports ----------------------------
# For logging errors and capturing stack traces
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Service to validate JWT token & Redis usage for account verification
from .account_verification_service import account_verification_service

# Service to mark users as verified in DB
from .user_verification_service import user_verification_service

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- Account Verification Handler Class ----------------------------
class AccountVerificationHandler:
    """
    Handles user account verification via email tokens.

    Flow:
    1. Validate JWT token and check Redis for single-use.
    2. Extract email from token payload.
    3. Mark user as verified using UserVerificationService.
    4. Return response indicating success or failure.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self):
        # Assign internal services to instance variables
        self.account_verification_service = account_verification_service
        self.user_verification_service = user_verification_service

    # ---------------------------- Main Verification Method ----------------------------
    async def handle_account_verification(self, token: str):
        """
        Verify an account using the token from the email.

        Parameters:
        - token: JWT token sent to user for account verification

        Returns:
        - tuple: (response_dict, status_code)
        """
        try:
            # ---------------------------- Verify Token ----------------------------
            # Validate the token and check Redis for single-use
            payload = await self.account_verification_service.verify_token(token)
            if not payload:
                return {"error": "Invalid, expired, or already used verification token"}, 400

            # Extract email from token payload
            email = payload.get("email")
            if not email:
                return {"error": "Malformed token payload"}, 400

            # ---------------------------- Mark User Verified ----------------------------
            # Use the new service to mark the user as verified
            updated = await self.user_verification_service.mark_user_verified(email)
            if updated:
                return {"message": f"Account verified successfully for {email}."}, 200
            else:
                return {"error": "User not found or already verified"}, 400

        except Exception:
            # Log unexpected errors for debugging
            logger.error("Error during account verification:\n%s", traceback.format_exc())
            return {"error": "Internal Server Error"}, 500

# ---------------------------- Instantiate AccountVerificationHandler ----------------------------
account_verification_handler = AccountVerificationHandler()
