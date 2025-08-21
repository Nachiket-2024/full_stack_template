# ---------------------------- External Imports ----------------------------
# For logging and handling exceptions
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# OAuth service for code-to-token exchange and user info
from .oauth2_service import oauth2_service

# ---------------------------- Logger Setup ----------------------------
# Create a logger for this module
logger = logging.getLogger(__name__)

# ---------------------------- OAuth2 Login Handler Class ----------------------------
class OAuth2LoginHandler:
    """
    Class to encapsulate the Google OAuth2 login flow.
    Handles token exchange, user info retrieval,
    and login/creation of users in the database.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self):
        # Assign the internal service to an instance variable
        self.oauth2_service = oauth2_service

    # ---------------------------- Main Login Method ----------------------------
    async def handle_oauth2_login(self, query_params: dict):
        """
        Handle Google OAuth2 redirect flow:
        1. Exchange authorization code for access token
        2. Get user info from Google
        3. Login or create user in DB
        4. Return JWT tokens for frontend redirect

        Parameters:
        - query_params: Query parameters from OAuth2 callback (e.g., code)

        Returns:
        - tuple: (jwt_tokens_dict, status_code)
        """
        try:
            # ---------------------------- Get Authorization Code ----------------------------
            # Extract 'code' parameter from query
            code = query_params.get("code")
            if not code:
                return {"error": "Missing authorization code"}, 400

            # ---------------------------- Exchange Code for Access Token ----------------------------
            # Exchange the authorization code for access tokens from Google
            token_data = await self.oauth2_service.exchange_code_for_tokens(code)
            if not token_data or "access_token" not in token_data:
                return {"error": "Failed to exchange code for access token"}, 400

            access_token_google = token_data["access_token"]

            # ---------------------------- Fetch User Info from Google ----------------------------
            # Get user information from Google using the access token
            user_info = await self.oauth2_service.get_user_info(access_token_google)
            if not user_info or "email" not in user_info:
                return {"error": "Failed to fetch user info from Google"}, 400

            # ---------------------------- Login or Create User ----------------------------
            # Login the user or create a new user in the DB
            jwt_tokens = await self.oauth2_service.login_or_create_user(user_info)
            if not jwt_tokens:
                return {"error": "Failed to login or create user"}, 500

            # ---------------------------- Return JWT Tokens for Redirect ----------------------------
            return jwt_tokens, 200

        except Exception:
            # Log the full traceback in case of errors
            logger.error("Error during OAuth2 login logic:\n%s", traceback.format_exc())
            return {"error": "Internal Server Error"}, 500


# ---------------------------- Instantiate OAuth2LoginHandler ----------------------------
oauth2_login_handler = OAuth2LoginHandler()
