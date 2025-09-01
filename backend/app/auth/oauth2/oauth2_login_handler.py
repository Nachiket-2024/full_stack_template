# ---------------------------- External Imports ----------------------------
# Logging module for tracking errors and events
import logging

# Module to capture full stack traces for debugging exceptions
import traceback

# FastAPI response class to redirect users
from fastapi.responses import RedirectResponse

# Async SQLAlchemy session for database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Settings for backend URL, frontend URL, and Google OAuth2 credentials
from ...core.settings import settings

# OAuth2 service providing token exchange, user info, and login/create functions
from .oauth2_service import oauth2_service

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- OAuth Handler Class ----------------------------
# Handler class to manage Google OAuth2 login flow
class OAuth2LoginHandler:
    """
    Handler for Google OAuth2 login:
    - Builds Google authorization URL and redirects user
    - Handles OAuth2 callback
    - Calls service methods individually
    - Sets JWT tokens in HTTP-only cookies
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize handler with OAuth2 service instance
    def __init__(self):
        self.oauth2_service = oauth2_service

    # ---------------------------- OAuth2 Login Initiation ----------------------------
    # Construct Google OAuth2 authorization URL and redirect user
    async def handle_oauth2_login_initiate(self):
        """
        Constructs Google OAuth2 authorization URL and redirects user.
        Returns:
        - RedirectResponse to Google login page
        """
        try:
            # Google OAuth2 authorization endpoint
            google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
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

            # Redirect user to Google login page
            return RedirectResponse(url=auth_url)

        except Exception:
            # Log errors during OAuth2 login initiation
            logger.error("Error initiating OAuth2 login:\n%s", traceback.format_exc())
            # Redirect to frontend login page
            return RedirectResponse(
                url=f"{settings.FRONTEND_BASE_URL}/login"
            )

    # ---------------------------- OAuth2 Callback Handler ----------------------------
    # Handle OAuth2 callback and set JWT tokens in HTTP-only cookies
    async def handle_oauth2_callback(self, code: str, db: AsyncSession):
        """
        Handles OAuth2 callback:
        - Exchanges code for Google tokens
        - Fetches user info
        - Logs in or creates user
        - Sets JWT tokens in HTTP-only cookies
        """
        try:
            # Callback URL for Google OAuth2
            redirect_uri = f"{settings.BACKEND_BASE_URL}/auth/oauth2/callback/google"

            # Exchange code for tokens using handler-provided credentials
            token_data = await self.oauth2_service.exchange_code_for_tokens(
                code,
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                redirect_uri=redirect_uri
            )
            if not token_data or "access_token" not in token_data:
                return RedirectResponse(
                    url=f"{settings.FRONTEND_BASE_URL}/login"
                )

            access_token_google = token_data["access_token"]

            # Fetch user info from Google
            user_info = await self.oauth2_service.get_user_info(access_token_google)
            if not user_info or "email" not in user_info:
                return RedirectResponse(
                    url=f"{settings.FRONTEND_BASE_URL}/login"
                )

            # Login or create user and generate JWT tokens
            jwt_tokens = await self.oauth2_service.login_or_create_user(db, user_info)
            if not jwt_tokens or "access_token" not in jwt_tokens:
                return RedirectResponse(
                    url=f"{settings.FRONTEND_BASE_URL}/login"
                )

            # ---------------------------- Set Tokens in HTTP-only Cookies ----------------------------
            # Prepare redirect response to dashboard
            response = RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/dashboard")
            # Set access token cookie
            response.set_cookie(
                key="access_token",
                value=jwt_tokens["access_token"],
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=3600
            )
            # Set refresh token cookie
            response.set_cookie(
                key="refresh_token",
                value=jwt_tokens["refresh_token"],
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=2592000
            )

            # Return response with cookies set
            return response

        except Exception:
            # Log errors during OAuth2 callback handling
            logger.error("Error handling OAuth2 callback:\n%s", traceback.format_exc())
            # Redirect to frontend login page
            return RedirectResponse(
                url=f"{settings.FRONTEND_BASE_URL}/login"
            )

# ---------------------------- Instantiate OAuthHandler ----------------------------
# Create a singleton instance of OAuth2LoginHandler for reuse
oauth2_login_handler = OAuth2LoginHandler()
