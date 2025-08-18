# ---------------------------- External Imports ----------------------------
# Async HTTP requests
import httpx

# For logging and traceback
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Load Gmail OAuth2 credentials
from ...core.settings import settings

# JWT handling service
from .jwt_service import jwt_service

# Password service (for temporary password if new user)
from .password_service import password_service

# Database CRUDs for roles
from ...role1.role1_crud import role1_crud
from ...role2.role2_crud import role2_crud
from ...admin.admin_crud import admin_crud

# ---------------------------- Logger Setup ----------------------------
# Configure logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- OAuth Service ----------------------------
class OAuthService:
    """
    Service to handle Gmail OAuth2 login flow and token exchange,
    with automatic default role assignment for new users.
    """

    # ---------------------------- Exchange Code for Tokens ----------------------------
    @staticmethod
    async def exchange_code_for_tokens(code: str) -> dict | None:
        """
        Exchange authorization code for Google access and refresh tokens.
        """
        try:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": settings.GMAIL_CLIENT_ID,
                "client_secret": settings.GMAIL_CLIENT_SECRET,
                "redirect_uri": settings.GMAIL_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(token_url, data=data)
                resp.raise_for_status()
                tokens = resp.json()
                return tokens
        except Exception:
            logger.error("Error exchanging code for tokens:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Get User Info ----------------------------
    @staticmethod
    async def get_user_info(access_token: str) -> dict | None:
        """
        Fetch the user's email and name from Google using the access token.
        """
        try:
            userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            async with httpx.AsyncClient() as client:
                resp = await client.get(userinfo_url, headers=headers)
                resp.raise_for_status()
                return resp.json()
        except Exception:
            logger.error("Error fetching user info:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Login or Create User ----------------------------
    @staticmethod
    async def login_or_create_user(user_info: dict) -> dict | None:
        """
        Login existing user or create a new one with default role2 if first-time login.
        Returns JWT access & refresh tokens.
        """
        try:
            email = user_info.get("email")
            name = user_info.get("name", "Unknown")

            # Check all roles to find existing user
            for role, crud in [("admin", admin_crud), ("role1", role1_crud), ("role2", role2_crud)]:
                user = await crud.get_by_email(email)
                if user:
                    user_role = role
                    crud_instance = crud
                    break
            else:
                # New user: assign role2 by default
                user_role = "role2"
                crud_instance = role2_crud
                # Generate temporary hashed password
                temp_pass = await password_service.hash_password("default_temp_password")
                user_data = {"name": name, "email": email, "hashed_password": temp_pass}
                user = await crud_instance.create(user_data)

            # Generate JWT tokens
            access_token = await jwt_service.create_access_token(email, user_role)
            refresh_token = await jwt_service.create_refresh_token(email, user_role)
            return {"access_token": access_token, "refresh_token": refresh_token}

        except Exception:
            logger.error("Error in OAuth login or create:\n%s", traceback.format_exc())
            return None

# ---------------------------- Service Instance ----------------------------
# Single instance for global use
oauth_service = OAuthService()
