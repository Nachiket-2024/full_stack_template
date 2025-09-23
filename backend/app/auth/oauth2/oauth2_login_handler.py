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
        # Assign OAuth2 service instance
        self.oauth2_service = oauth2_service

    # ---------------------------- OAuth2 Login Initiation ----------------------------
    # Async method to start OAuth2 login by redirecting to Google
    async def handle_oauth2_login_initiate(self):
        """
        Input:
            1. None

        Process:
            1. Define Google OAuth2 authorization endpoint URL.
            2. Define required OAuth2 scopes.
            3. Define redirect URI for callback.
            4. Construct full authorization URL with query parameters.
            5. Redirect user to Google login page.
            6. Redirect to frontend login page on error.

        Output:
            1. RedirectResponse: User redirected to Google login page or frontend login on error.
        """
        try:
            # Step 1: Define Google OAuth2 authorization endpoint URL
            google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"

            # Step 2: Define required OAuth2 scopes
            scopes = "openid email profile"

            # Step 3: Define redirect URI for callback
            redirect_uri = f"{settings.BACKEND_BASE_URL}/auth/oauth2/callback/google"

            # Step 4: Construct full authorization URL with query parameters
            auth_url = (
                f"{google_auth_url}?response_type=code"
                f"&client_id={settings.GOOGLE_CLIENT_ID}"
                f"&redirect_uri={redirect_uri}"
                f"&scope={scopes.replace(' ', '%20')}"
                f"&access_type=offline"
                f"&prompt=consent"
            )

            # Step 5: Redirect user to Google login page
            return RedirectResponse(url=auth_url)

        except Exception:
            # Handle exceptions and log errors
            logger.error("Error initiating OAuth2 login:\n%s", traceback.format_exc())

            # Step 6: Redirect to frontend login page on error
            return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login")

    # ---------------------------- OAuth2 Callback Handler ----------------------------
    # Async method to handle OAuth2 callback from Google
    async def handle_oauth2_callback(self, code: str, db: AsyncSession):
        """
        Input:
            1. code (str): Authorization code from Google.
            2. db (AsyncSession): Database session.

        Process:
            1. Build redirect URI for OAuth2 callback.
            2. Exchange code for Google access tokens.
            3. Validate token exchange result.
            4. Fetch user info from Google.
            5. Validate user info.
            6. Authenticate existing user or create a new user, then generate JWT tokens.
            7. Validate generated JWT tokens.
            8. Create redirect response to dashboard.
            9. Set JWT tokens in secure HTTP-only cookies.
            10. Return redirect response.
            11. Redirect to frontend login page on error.

        Output:
            1. RedirectResponse: User redirected to dashboard with cookies set or frontend login on error.
        """
        try:
            # Step 1: Build redirect URI for OAuth2 callback
            redirect_uri = f"{settings.BACKEND_BASE_URL}/auth/oauth2/callback/google"

            # Step 2: Exchange code for Google access tokens
            token_data = await self.oauth2_service.exchange_code_for_tokens(
                code,
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                redirect_uri=redirect_uri
            )

            # Step 3: Validate token exchange result
            if not token_data or "access_token" not in token_data:
                return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login")

            access_token_google = token_data["access_token"]

            # Step 4: Fetch user info from Google
            user_info = await self.oauth2_service.get_user_info(access_token_google)

            # Step 5: Validate user info
            if not user_info or "email" not in user_info:
                return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login")

            # Step 6: Authenticate existing user or create a new user, then generate JWT tokens
            jwt_tokens = await self.oauth2_service.login_or_create_user(db, user_info)

            # Step 7: Validate generated JWT tokens
            if not jwt_tokens or "access_token" not in jwt_tokens:
                return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login")

            # Step 8: Create redirect response to dashboard
            response = RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/dashboard")

            # Step 9: Set JWT tokens in secure HTTP-only cookies
            token_cookie_handler.set_tokens_in_cookies(response, jwt_tokens)

            # Step 10: Return redirect response
            return response

        except Exception:
            # Handle exceptions and log errors
            logger.error("Error handling OAuth2 callback:\n%s", traceback.format_exc())

            # Step 11: Redirect to frontend login page on error
            return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login")


# ---------------------------- Instantiate OAuthHandler ----------------------------
# Singleton instance of OAuth2LoginHandler for reuse
oauth2_login_handler = OAuth2LoginHandler()
