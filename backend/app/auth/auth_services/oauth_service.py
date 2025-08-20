# ---------------------------- External Imports ----------------------------
# Async HTTP requests
import httpx

# For logging and handling exceptions
import logging
import traceback

# For concurrent async calls
import asyncio  

# ---------------------------- Internal Imports ----------------------------
# Load Gmail OAuth2 credentials
from ...core.settings import settings

# JWT handling service
from .jwt_service import jwt_service

# Centralized role CRUD table and default role
from ...core.role_tables import ROLE_TABLES, DEFAULT_ROLE

# ---------------------------- Logger Setup ----------------------------
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
        try:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(token_url, data=data)
                resp.raise_for_status()
                return resp.json()
        except Exception:
            logger.error("Error exchanging code for tokens:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Get User Info ----------------------------
    @staticmethod
    async def get_user_info(access_token: str) -> dict | None:
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
        Logs in an existing user or creates a new one with default role.
        Stores latest JWT tokens in DB.
        """
        try:
            email = user_info.get("email")
            name = user_info.get("name", "Unknown")

            user = None
            user_role = None
            crud_instance = None

            # ---------------------------- Search for Existing User ----------------------------
            for role, crud in ROLE_TABLES.items():
                user = await crud.get_by_email(email)
                if user:
                    user_role = role
                    crud_instance = crud
                    break

            # ---------------------------- Handle New User ----------------------------
            if not user:
                user_role = DEFAULT_ROLE
                crud_instance = ROLE_TABLES[user_role]
                user_data = {"name": name, "email": email}
                user = await crud_instance.create(user_data)

            # ---------------------------- Generate JWT Tokens ----------------------------
            access_token, refresh_token = await asyncio.gather(
                jwt_service.create_access_token(email, user_role),
                jwt_service.create_refresh_token(email, user_role)
            )

            # ---------------------------- Store Tokens in DB ----------------------------
            await crud_instance.update_by_email(email, {
                "access_token": access_token,
                "refresh_token": refresh_token
            })

            return {"access_token": access_token, "refresh_token": refresh_token}

        except Exception:
            logger.error("Error in OAuth login or create:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
oauth_service = OAuthService()
