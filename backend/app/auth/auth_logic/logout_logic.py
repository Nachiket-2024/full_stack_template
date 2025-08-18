# ---------------------------- External Imports ----------------------------
# For logging and exception handling
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Refresh token service to revoke tokens
from ..auth_services.refresh_token_service import refresh_token_service

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Logout Logic Function ----------------------------
async def handle_logout(refresh_token: str):
    """
    Handle user logout by revoking their refresh token.

    Parameters:
    - refresh_token: The user's refresh token to be revoked

    Returns:
    - tuple: (response_dict, status_code)
      - If successful, returns success message and 200
      - If token invalid or already revoked, returns error and 400
      - On exception, returns error and 500
    """
    try:
        # ---------------------------- Revoke Token ----------------------------
        success = await refresh_token_service.revoke_refresh_token(refresh_token)

        if not success:
            # Token is invalid or already revoked
            return {"error": "Invalid refresh token or already revoked"}, 400

        # Logout successful
        return {"message": "Logged out successfully"}, 200

    except Exception:
        # Catch any unexpected errors and log for debugging
        logger.error("Error during logout logic:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500
