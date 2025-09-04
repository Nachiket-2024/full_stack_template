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
    """
    1. handle_oauth2_login_initiate - Redirect user to Google OAuth2 login page.
    2. handle_oauth2_callback - Handle OAuth2 callback, exchange code for tokens, authenticate user, and set cookies.
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize handler with OAuth2 service instance
    def __init__(self):
        # Assign OAuth2 service instance for token exchange and user login
        self.oauth2_service = oauth2_service

    # ---------------------------- OAuth2 Login Initiation ----------------------------
    # Async method to start OAuth2 login by redirecting to Google
    async def handle_oauth2_login_initiate(self):
        """
        Input:
            1. None

        Process:
            1. Build Google OAuth2 authorization URL with client_id, redirect_uri, scopes, access_type, and prompt.
            2. Redirect user to Google login page.

        Output:
            1. RedirectResponse: User redirected to Google login page or frontend login on error.
        """
        try:
            # ---------------------------- Build Authorization URL ----------------------------
            # Google OAuth2 authorization endpoint
            google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"

            # Scopes required for authentication
            scopes = "openid email profile"

            # Redirect URI for OAuth2 callback
            redirect_uri = f"{settings.BACKEND_BASE_URL}/auth/oauth2/callback/google"

            # Construct full authorization URL
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
        # Catch unexpected errors
        except Exception:
            # Log error with full traceback
            logger.error("Error initiating OAuth2 login:\n%s", traceback.format_exc())

            # Redirect to frontend login page on error
            return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login")

    # ---------------------------- OAuth2 Callback Handler ----------------------------
    # Async method to handle OAuth2 callback from Google
    async def handle_oauth2_callback(self, code: str, db: AsyncSession):
        """
        Input:
            1. code (str): Authorization code from Google.
            2. db (AsyncSession): Database session.

        Process:
            1. Build redirect_uri for callback.
            2. Exchange code for Google access tokens.
            3. Validate token exchange result.
            4. Fetch user info from Google.
            5. Validate user info.
            6. Authenticate or create user and generate JWT tokens.
            7. Validate JWT tokens.
            8. Set JWT tokens in secure HTTP-only cookies.
            9. Redirect user to dashboard.

        Output:
            1. RedirectResponse: User redirected to dashboard with cookies set or frontend login on error.
        """
        try:
            # ---------------------------- Build Redirect URI ----------------------------
            # Callback URL for OAuth2 redirect
            redirect_uri = f"{settings.BACKEND_BASE_URL}/auth/oauth2/callback/google"

            # ---------------------------- Exchange Code for Tokens ----------------------------
            # Use OAuth2 service to exchange code for tokens
            token_data = await self.oauth2_service.exchange_code_for_tokens(
                code,
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                redirect_uri=redirect_uri
            )

            # Validate token exchange
            if not token_data or "access_token" not in token_data:
                # Redirect to frontend login on failure
                return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login")

            # Extract Google access token
            access_token_google = token_data["access_token"]

            # ---------------------------- Fetch User Info ----------------------------
            # Retrieve user info from Google using access token
            user_info = await self.oauth2_service.get_user_info(access_token_google)

            # Validate user info
            if not user_info or "email" not in user_info:
                # Redirect to frontend login on invalid user info
                return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login")

            # ---------------------------- Login or Create User ----------------------------
            # Authenticate existing user or create new user, then generate JWT tokens
            jwt_tokens = await self.oauth2_service.login_or_create_user(db, user_info)

            # Validate generated JWT tokens
            if not jwt_tokens or "access_token" not in jwt_tokens:
                # Redirect to frontend login if JWT tokens are missing
                return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login")

            # ---------------------------- Set Tokens via TokenCookieHandler ----------------------------
            # Create redirect response to dashboard
            response = RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/dashboard")

            # Set JWT tokens in secure HTTP-only cookies
            token_cookie_handler.set_tokens_in_cookies(response, jwt_tokens)

            # Return response with cookies set
            return response

        # ---------------------------- Exception Handling ----------------------------
        # Catch unexpected errors
        except Exception:
            # Log full traceback for debugging
            logger.error("Error handling OAuth2 callback:\n%s", traceback.format_exc())

            # Redirect to frontend login page on error
            return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login")


# ---------------------------- Instantiate OAuthHandler ----------------------------
# Singleton instance of OAuth2LoginHandler for reuse
oauth2_login_handler = OAuth2LoginHandler()
