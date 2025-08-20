# ---------------------------- External Imports ----------------------------
# For logging errors and debugging
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Auth service to update user verification status in DB
from ..auth_services.auth_service import auth_service

# Account verification service to validate JWT token & Redis usage
from ..auth_services.account_verification_service import account_verification_service

# Centralized list of all role tables
from ...core.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)
# Set basic logging configuration (INFO level)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Verification Logic Function ----------------------------
async def handle_account_verification(token: str, table_name: str):
    """
    Verify an account using the token sent via email, for a specific role/table.

    Flow:
    1. Verify JWT token & check Redis for single-use.
    2. If valid, mark user as verified in the given role table.
    3. Return appropriate response.

    Parameters:
    - token: JWT token from verification email
    - table_name: Role table to update (must exist in ROLE_TABLES)

    Returns:
    - tuple: (response_dict, status_code)
    """
    try:
        # ---------------------------- Validate Table Name ----------------------------
        if table_name not in ROLE_TABLES:
            return {"error": "Invalid or unknown role/table"}, 400

        # ---------------------------- Verify Token ----------------------------
        payload = await account_verification_service.verify_token(token)
        if not payload:
            return {"error": "Invalid, expired, or already used verification token"}, 400

        # Extract user email from token payload
        email = payload.get("sub")
        if not email:
            return {"error": "Malformed token payload"}, 400

        # ---------------------------- Mark User Verified ----------------------------
        updated = await auth_service.mark_user_verified(email, table_name)
        if updated:
            return {"message": f"Account verified successfully for {table_name}."}, 200
        else:
            return {"error": "User not found or already verified"}, 400

    except Exception:
        # Log the full traceback for debugging purposes
        logger.error("Error during account verification:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500
