# ---------------------------- External Imports ----------------------------
# For logging and exception handling
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Refresh token service to revoke tokens
from ..token_logic.refresh_token_service import refresh_token_service

# ---------------------------- Logger Setup ----------------------------
# Logger for capturing errors in logout-all logic
logger = logging.getLogger(__name__)

# ---------------------------- Logout All Handler Class ----------------------------
class LogoutAllHandler:
    """
    Class to handle logging out a user from all devices.
    Delegates token verification and revocation to the refresh token service.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self):
        # Assign the refresh token service to an instance variable
        self.refresh_token_service = refresh_token_service

    # ---------------------------- Main Logout All Method ----------------------------
    async def handle_logout_all(self, refresh_token: str, db):
        """
        Logs the user out from all devices by revoking all refresh tokens
        associated with the user identified by the provided refresh token.

        Parameters:
        - refresh_token: The refresh token provided by the client
        - db: AsyncSession for database operations

        Returns:
        - tuple: (response_dict, status_code)
        """
        try:
            # ---------------------------- Revoke All Tokens ----------------------------
            # Delegate revocation logic to the service
            revoked_count = await self.refresh_token_service.revoke_all_tokens(refresh_token, db=db)

            # ---------------------------- Check Revocation Result ----------------------------
            if revoked_count == 0:
                # Token invalid, malformed, or no tokens found
                return {"error": "Invalid refresh token or no tokens to revoke"}, 400

            # Logout successful
            return {"message": f"Logged out from {revoked_count} devices"}, 200

        except Exception:
            # Catch any unexpected errors and log the full traceback
            logger.error("Error during logout-all logic:\n%s", traceback.format_exc())
            return {"error": "Internal Server Error"}, 500


# ---------------------------- Instantiate LogoutAllHandler ----------------------------
logout_all_handler = LogoutAllHandler()
