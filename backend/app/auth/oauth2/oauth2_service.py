# ---------------------------- External Imports ----------------------------
# Async HTTP client for making HTTP requests to Google APIs
import httpx

# Logging module for tracking errors and events
import logging

# Module to capture full stack traces for debugging exceptions
import traceback

# Asyncio for concurrent async operations
import asyncio

# ---------------------------- Internal Imports ----------------------------
# Import JWT service to generate access and refresh tokens
from ..token_logic.jwt_service import jwt_service

# Import role tables and default role for user management
from ...access_control.role_tables import ROLE_TABLES, DEFAULT_ROLE

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- OAuth2 Service ----------------------------
# Service class handling Google OAuth2 operations
class OAuth2Service:

    # ---------------------------- Exchange Code for Tokens ----------------------------
    # Exchange authorization code for access and refresh tokens from Google
    @staticmethod
    async def exchange_code_for_tokens(code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict | None:

        try:
            # Google token endpoint
            token_url = "https://oauth2.googleapis.com/token"

            # Payload for POST request
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }

            # Async HTTP POST request to exchange code for tokens
            async with httpx.AsyncClient() as client:
                resp = await client.post(token_url, data=data)
                resp.raise_for_status()
                return resp.json()

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log errors with full traceback
            logger.error("Error exchanging code for tokens:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Get User Info ----------------------------
    # Retrieve user profile information from Google using access token
    @staticmethod
    async def get_user_info(access_token: str) -> dict | None:

        try:
            # Google userinfo endpoint
            userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}

            # Async HTTP GET request to fetch user info
            async with httpx.AsyncClient() as client:
                resp = await client.get(userinfo_url, headers=headers)
                resp.raise_for_status()
                return resp.json()

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log errors with full traceback
            logger.error("Error fetching user info:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Login or Create User ----------------------------
    # Authenticate existing user or create new user and generate JWT tokens
    @staticmethod
    async def login_or_create_user(db, user_info: dict) -> dict | None:
        
        try:
            # Extract email and name from user info
            email = user_info.get("email")
            name = user_info.get("name", "Unknown")

            user = None
            user_role = None
            crud_instance = None

            # Check all role tables for existing user
            for role, crud in ROLE_TABLES.items():
                user = await crud.get_by_email(db, email)
                if user:
                    user_role = role
                    crud_instance = crud
                    break

            # If user does not exist, create new with default role
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

            # ---------------------------- Update Tokens in Database ----------------------------
            await crud_instance.update_by_email(db, email, {
                "access_token": access_token,
                "refresh_token": refresh_token
            })

            # Return the generated tokens
            return {"access_token": access_token, "refresh_token": refresh_token}

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log any exception that occurs during login or creation
            logger.error("Error in login or create user:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
# Singleton instance of OAuth2Service for reuse in handlers
oauth2_service = OAuth2Service()
