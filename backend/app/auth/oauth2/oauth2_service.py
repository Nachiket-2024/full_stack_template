# ---------------------------- External Imports ----------------------------
# Async HTTP client for interacting with Google OAuth2 endpoints
import httpx

# Logging module for tracking errors and events
import logging

# Capture full stack traces for debugging exceptions
import traceback

# Utilities to run multiple async coroutines concurrently
import asyncio  

# ---------------------------- Internal Imports ----------------------------
# Application settings containing OAuth2 credentials and redirect URIs
from ...core.settings import settings

# JWT service for generating access and refresh tokens
from ..token_logic.jwt_service import jwt_service

# Central role-based CRUD tables and the default role for new users
from ...access_control.role_tables import ROLE_TABLES, DEFAULT_ROLE

# ---------------------------- Logger Setup ----------------------------
# Module-level logger
logger = logging.getLogger(__name__)

# ---------------------------- OAuth2 Service ----------------------------
# Service class to manage Gmail OAuth2 login and user creation
class OAuth2Service:
    """
    Service to handle Gmail OAuth2 login flow and token exchange,
    with automatic default role assignment for new users.
    """

    # ---------------------------- Exchange Code for Tokens ----------------------------
    # Static async method to exchange OAuth2 authorization code for access and refresh tokens
    @staticmethod
    async def exchange_code_for_tokens(code: str) -> dict | None:
        try:
            # Google OAuth2 token endpoint
            token_url = "https://oauth2.googleapis.com/token"
            
            # Payload required by Google to exchange code for tokens
            data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            
            # Async HTTP POST request to exchange code for tokens
            async with httpx.AsyncClient() as client:
                resp = await client.post(token_url, data=data)
                resp.raise_for_status()  # Raise exception if HTTP error occurs
                return resp.json()
        except Exception:
            # Log error with stack trace and return None
            logger.error("Error exchanging code for tokens:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Get User Info ----------------------------
    # Static async method to fetch user profile information using access token
    @staticmethod
    async def get_user_info(access_token: str) -> dict | None:
        try:
            # Google endpoint to fetch user profile info
            userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
            
            # Authorization header with bearer token
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Async HTTP GET request to fetch user info
            async with httpx.AsyncClient() as client:
                resp = await client.get(userinfo_url, headers=headers)
                resp.raise_for_status()  # Raise exception if HTTP error occurs
                return resp.json()
        except Exception:
            # Log error with stack trace and return None
            logger.error("Error fetching user info:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Login or Create User ----------------------------
    # Static async method to log in an existing user or create a new user with default role
    @staticmethod
    async def login_or_create_user(db, user_info: dict) -> dict | None:
        """
        Logs in an existing user or creates a new one with default role.
        Stores latest JWT tokens in the database.
        """
        try:
            # Extract email and name from user info
            email = user_info.get("email")
            name = user_info.get("name", "Unknown")

            # Initialize variables for user lookup
            user = None
            user_role = None
            crud_instance = None

            # ---------------------------- Search for Existing User ----------------------------
            # Iterate through all roles to find user by email
            for role, crud in ROLE_TABLES.items():
                user = await crud.get_by_email(db, email)   
                if user:
                    user_role = role
                    crud_instance = crud
                    break

            # ---------------------------- Handle New User ----------------------------
            # If user does not exist, assign default role and create a new user
            if not user:
                user_role = DEFAULT_ROLE
                crud_instance = ROLE_TABLES[user_role]
                user_data = {"name": name, "email": email}
                user = await crud_instance.create(db, user_data)   

            # ---------------------------- Generate JWT Tokens ----------------------------
            # Generate access and refresh tokens concurrently
            access_token, refresh_token = await asyncio.gather(
                jwt_service.create_access_token(email, user_role),
                jwt_service.create_refresh_token(email, user_role)
            )

            # ---------------------------- Store Tokens in DB ----------------------------
            # Update the user's token fields in the database
            await crud_instance.update_by_email(db, email, {   
                "access_token": access_token,
                "refresh_token": refresh_token
            })

            # Return structured token response
            return {"access_token": access_token, "refresh_token": refresh_token}

        except Exception:
            # Log any exception during login or user creation
            logger.error("Error in OAuth2 login or create:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
# Singleton instance to be used for OAuth2 login operations
oauth2_service = OAuth2Service()
