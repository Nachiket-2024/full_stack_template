# ---------------------------- External Imports ----------------------------
# Import logging module for tracking errors and events
import logging

# Import traceback module to capture full stack traces for debugging exceptions
import traceback

# Import FastAPI RedirectResponse for redirecting users
from fastapi.responses import RedirectResponse

# Import AsyncSession from SQLAlchemy for async database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Import settings for backend URL, frontend URL, and Google OAuth2 credentials
from ...core.settings import settings

# Import OAuth2 service providing token exchange, user info, and login/create functions
from .oauth2_service import oauth2_service

# Import cookie handler to centralize token cookie management
from ..token_logic.token_cookie_handler import token_cookie_handler

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- OAuth Handler Class ----------------------------
# Define handler class to manage Google OAuth2 login flow
class OAuth2LoginHandler:

    # ---------------------------- Constructor ----------------------------
    # Initialize handler with OAuth2 service instance
    def __init__(self):
        self.oauth2_service = oauth2_service

    # ---------------------------- OAuth2 Login Initiation ----------------------------
    # Construct Google OAuth2 authorization URL and redirect user
    async def handle_oauth2_login_initiate(self):
        # Use try-except to handle runtime errors
        try:
            # ---------------------------- Build Authorization URL ----------------------------
            # Google OAuth2 authorization endpoint
            google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
            # Required scopes for authentication
            scopes = "openid email profile"
            # Callback URL after Google authentication
            redirect_uri = f"{settings.BACKEND_BASE_URL}/auth/oauth2/callback/google"

            # Build full authorization URL with query parameters
            auth_url = (
                f"{google_auth_url}?response_type=code"
                f"&client_id={settings.GOOGLE_CLIENT_ID}"
                f"&redirect_uri={redirect_uri}"
                f"&scope={scopes.replace(' ', '%20')}"
                f"&access_type=offline"
                f"&prompt=consent"
            )

            # ---------------------------- Redirect User ----------------------------
            # Redirect user to Google login page
            return RedirectResponse(url=auth_url)

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log errors during OAuth2 login initiation
            logger.error("Error initiating OAuth2 login:\n%s", traceback.format_exc())
            # Redirect to frontend login page if failure occurs
            return RedirectResponse(
                url=f"{settings.FRONTEND_BASE_URL}/login"
            )

    # ---------------------------- OAuth2 Callback Handler ----------------------------
    # Handle OAuth2 callback, exchange code for tokens, and set JWT cookies
    async def handle_oauth2_callback(self, code: str, db: AsyncSession):
        # Use try-except to handle runtime errors
        try:
            # ---------------------------- Build Redirect URI ----------------------------
            # Callback URL for Google OAuth2
            redirect_uri = f"{settings.BACKEND_BASE_URL}/auth/oauth2/callback/google"

            # ---------------------------- Exchange Code for Tokens ----------------------------
            # Exchange authorization code for tokens
            token_data = await self.oauth2_service.exchange_code_for_tokens(
                code,
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                redirect_uri=redirect_uri
            )

            # Validate token exchange result
            if not token_data or "access_token" not in token_data:
                return RedirectResponse(
                    url=f"{settings.FRONTEND_BASE_URL}/login"
                )

            # Extract access token from response
            access_token_google = token_data["access_token"]

            # ---------------------------- Fetch User Info ----------------------------
            # Get user info from Google using access token
            user_info = await self.oauth2_service.get_user_info(access_token_google)

            # Validate user info
            if not user_info or "email" not in user_info:
                return RedirectResponse(
                    url=f"{settings.FRONTEND_BASE_URL}/login"
                )

            # ---------------------------- Login or Create User ----------------------------
            # Authenticate or create user and generate JWT tokens
            jwt_tokens = await self.oauth2_service.login_or_create_user(db, user_info)

            # Validate JWT tokens
            if not jwt_tokens or "access_token" not in jwt_tokens:
                return RedirectResponse(
                    url=f"{settings.FRONTEND_BASE_URL}/login"
                )

            # ---------------------------- Set Tokens via TokenCookieHandler ----------------------------
            # Redirect to dashboard after successful login
            response = RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/dashboard")
            # Set JWT tokens into cookies securely
            token_cookie_handler.set_tokens_in_cookies(response, jwt_tokens)

            # Return response with cookies set
            return response

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log errors during OAuth2 callback handling
            logger.error("Error handling OAuth2 callback:\n%s", traceback.format_exc())
            # Redirect to frontend login page if failure occurs
            return RedirectResponse(
                url=f"{settings.FRONTEND_BASE_URL}/login"
            )


# ---------------------------- Instantiate OAuthHandler ----------------------------
# Create a singleton instance of OAuth2LoginHandler for reuse
oauth2_login_handler = OAuth2LoginHandler()
