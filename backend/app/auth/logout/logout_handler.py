# ---------------------------- External Imports ----------------------------
# For logging and exception handling
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Refresh token service to revoke tokens
from ..token_logic.refresh_token_service import refresh_token_service

# ---------------------------- Logger Setup ----------------------------
# Create a logger for this module
logger = logging.getLogger(__name__)

# ---------------------------- Logout Handler Class ----------------------------
class LogoutHandler:
    """
    Class to handle user logout operations.
    Encapsulates logic to revoke refresh tokens and handle errors.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self):
        # Assign the refresh token service to an instance variable
        self.refresh_token_service = refresh_token_service

    # ---------------------------- Main Logout Method ----------------------------
    async def handle_logout(self, refresh_token: str):
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
            # Attempt to revoke the refresh token via the service
            success = await self.refresh_token_service.revoke_refresh_token(refresh_token)

            # ---------------------------- Check Revocation Result ----------------------------
            if not success:
                # Token is invalid or already revoked
                return {"error": "Invalid refresh token or already revoked"}, 400

            # Logout successful
            return {"message": "Logged out successfully"}, 200

        except Exception:
            # Catch any unexpected errors and log the full traceback
            logger.error("Error during logout logic:\n%s", traceback.format_exc())
            return {"error": "Internal Server Error"}, 500


# ---------------------------- Instantiate LogoutHandler ----------------------------
logout_handler = LogoutHandler()
