# ---------------------------- External Imports ----------------------------
# Import async HTTP client for Google API requests
import httpx

# Import logging module for tracking errors and events
import logging

# Import traceback module to capture full stack traces for debugging exceptions
import traceback

# Import asyncio for concurrent asynchronous operations
import asyncio

# Import JSON module for serialization
import json

# ---------------------------- Internal Imports ----------------------------
# Import JWT service to generate access and refresh tokens
from ..token_logic.jwt_service import jwt_service

# Import role tables for user management
from ...access_control.role_tables import ROLE_TABLES, DEFAULT_ROLE

# Import singleton Redis client
from ...redis.client import redis_client

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- OAuth2 Service ----------------------------
class OAuth2Service:
    """
    1. exchange_code_for_tokens - Exchange authorization code for Google access and refresh tokens.
    2. get_user_info - Retrieve Google user profile information using access token.
    3. login_or_create_user - Authenticate existing user or create new user and generate JWT tokens, persist them in Redis with multi-device support.
    """

    # ---------------------------- Exchange Code for Tokens ----------------------------
    @staticmethod
    async def exchange_code_for_tokens(code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict | None:
        """
        Input:
            1. code (str) - Google authorization code
            2. client_id (str) - OAuth2 client ID
            3. client_secret (str) - OAuth2 client secret
            4. redirect_uri (str) - Redirect URI used in OAuth2 flow

        Process:
            1. Prepare POST payload with code and credentials.
            2. Send POST request to Google OAuth2 token endpoint asynchronously.
            3. Parse and return JSON response containing tokens.

        Output:
            1. dict | None - Token dictionary or None on failure
        """
        try:
            # Step 1: Prepare POST payload with code and credentials
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }

            # Step 2: Send POST request to Google OAuth2 token endpoint asynchronously
            async with httpx.AsyncClient() as client:
                resp = await client.post(token_url, data=data)
                resp.raise_for_status()  # Step 2a: Raise exception for non-success status codes

                # Step 3: Parse and return JSON response containing tokens
                return resp.json()

        except Exception:
            logger.error("Error exchanging code for tokens:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Get User Info ----------------------------
    @staticmethod
    async def get_user_info(access_token: str) -> dict | None:
        """
        Input:
            1. access_token (str) - Google access token

        Process:
            1. Prepare authorization headers with Bearer token.
            2. Send GET request to Google userinfo endpoint asynchronously.
            3. Parse and return JSON response containing user info.

        Output:
            1. dict | None - User info dictionary or None on failure
        """
        try:
            # Step 1: Prepare authorization headers with Bearer token
            userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}

            # Step 2: Send GET request to Google userinfo endpoint asynchronously
            async with httpx.AsyncClient() as client:
                resp = await client.get(userinfo_url, headers=headers)
                resp.raise_for_status()  # Step 2a: Raise exception for non-success status codes

                # Step 3: Parse and return JSON response containing user info
                return resp.json()

        except Exception:
            logger.error("Error fetching user info:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Login or Create User ----------------------------
    @staticmethod
    async def login_or_create_user(db, user_info: dict, device_id: str | None = None) -> dict | None:
        """
        Input:
            1. db - Async database session/connection
            2. user_info (dict) - Google user info dictionary
            3. device_id (str | None) - Optional device identifier for multi-device token storage

        Process:
            1. Extract email and name from user_info.
            2. Search existing users in all role tables.
            3. Create new user if not found with default role and set is_verified=True.
            4. Generate access and refresh JWT tokens concurrently.
            5. Store tokens in Redis list under user's email for multi-device support.
            6. Return tokens if successful.

        Output:
            1. dict | None - Dictionary with access_token and refresh_token or None on failure
        """
        try:
            # Step 1: Extract email and name from user_info
            email = user_info.get("email")
            name = user_info.get("name", "Unknown")

            # Step 2: Search existing users in all role tables
            user, user_role, crud_instance = None, None, None
            for role, crud in ROLE_TABLES.items():
                user = await crud.get_by_email(db, email)
                if user:
                    user_role, crud_instance = role, crud
                    break

            # Step 3: Create new user if not found with default role and set is_verified=True
            if not user:
                user_role = DEFAULT_ROLE
                crud_instance = ROLE_TABLES[user_role]
                user_data = {"name": name, "email": email, "is_verified": True}
                user = await crud_instance.create(db, user_data)

            # Step 4: Generate access and refresh JWT tokens concurrently
            access_token, refresh_token = await asyncio.gather(
                jwt_service.create_access_token(email, user_role),
                jwt_service.create_refresh_token(email, user_role)
            )

            # Step 5: Store tokens in Redis list under user's email for multi-device support
            token_entry = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "device_id": device_id or "unknown"
            }
            
            redis_key = f"user_tokens:{email}"
            await redis_client.rpush(redis_key, json.dumps(token_entry))

            # Step 6: Return tokens if successful
            return {"access_token": access_token, "refresh_token": refresh_token}

        except Exception:
            logger.error("Error in login or create user:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
# Singleton instance of OAuth2Service for external use
oauth2_service = OAuth2Service()
