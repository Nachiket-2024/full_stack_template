# ---------------------------- External Imports ----------------------------
# Import async HTTP client for Google API requests
import httpx

# Import logging module for tracking errors and events
import logging

# Import traceback module to capture full stack traces for debugging exceptions
import traceback

# Import asyncio for concurrent asynchronous operations
import asyncio

# ---------------------------- Internal Imports ----------------------------
# Import JWT service to generate access and refresh tokens
from ..token_logic.jwt_service import jwt_service

# Import role tables and token tables for user management
from ...access_control.role_tables import ROLE_TABLES, DEFAULT_ROLE, TOKEN_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- OAuth2 Service ----------------------------
class OAuth2Service:
    """
    1. exchange_code_for_tokens - Exchange authorization code for Google access and refresh tokens.
    2. get_user_info - Retrieve Google user profile information using access token.
    3. login_or_create_user - Authenticate existing user or create new user and generate JWT tokens, persist them in the token table.
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
        2. Send POST request to Google OAuth2 token endpoint.
        3. Return parsed JSON response if successful.
        4. Log error and return None if an exception occurs.

        Output:
        1. dict | None - Token dictionary or None on failure
        """
        try:
            # Define the Google OAuth2 token endpoint
            token_url = "https://oauth2.googleapis.com/token"

            # Prepare POST request payload
            data = {
                "code": code,                     # Authorization code from Google
                "client_id": client_id,           # OAuth2 client ID
                "client_secret": client_secret,   # OAuth2 client secret
                "redirect_uri": redirect_uri,     # Callback URI
                "grant_type": "authorization_code"  # OAuth2 grant type
            }
            
            # Make asynchronous POST request
            async with httpx.AsyncClient() as client:
                # Send POST request to exchange code for tokens
                resp = await client.post(token_url, data=data)

                # Raise exception for non-success status codes
                resp.raise_for_status()

                # Return response JSON containing tokens
                return resp.json()
            
        except Exception:
            # Log full traceback in case of error
            logger.error("Error exchanging code for tokens:\n%s", traceback.format_exc())

            # Return None if error occurs
            return None

    # ---------------------------- Get User Info ----------------------------
    @staticmethod
    async def get_user_info(access_token: str) -> dict | None:
        """
        Input:
        1. access_token (str) - Google access token

        Process:
        1. Prepare authorization headers.
        2. Send GET request to Google userinfo endpoint.
        3. Return parsed JSON response if successful.
        4. Log error and return None if an exception occurs.

        Output:
        1. dict | None - User info dictionary or None on failure
        """
        try:
            # Define Google userinfo endpoint
            userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"

            # Prepare headers with Bearer token
            headers = {"Authorization": f"Bearer {access_token}"}

            # Make asynchronous GET request
            async with httpx.AsyncClient() as client:
                # Send GET request to fetch user info
                resp = await client.get(userinfo_url, headers=headers)

                # Raise exception for non-success status codes
                resp.raise_for_status()

                # Return response JSON containing user info
                return resp.json()
            
        except Exception:
            # Log full traceback in case of error
            logger.error("Error fetching user info:\n%s", traceback.format_exc())

            # Return None if error occurs
            return None

    # ---------------------------- Login or Create User ----------------------------
    @staticmethod
    async def login_or_create_user(db, user_info: dict) -> dict | None:
        """
        Input:
        1. db - Async database session/connection
        2. user_info (dict) - Google user info dictionary

        Process:
        1. Extract email and name from user_info.
        2. Search existing users in all role tables.
        3. Create new user if not found with default role and set is_verified=True.
        4. Generate access and refresh JWT tokens.
        5. Always insert a new token record for each login (multi-device support).
        6. Return tokens if successful.
        7. Log error and return None if exception occurs.

        Output:
        1. dict | None - Dictionary with access_token and refresh_token or None on failure
        """
        try:
            # Extract email
            email = user_info.get("email")

            # Extract name or default to "Unknown"
            name = user_info.get("name", "Unknown")

            # Initialize placeholders
            user, user_role, crud_instance = None, None, None

            # Loop through role tables to find user by email
            for role, crud in ROLE_TABLES.items():
                # Attempt to get user by email
                user = await crud.get_by_email(db, email)

                # If user exists, store role and crud instance, then break
                if user:
                    user_role, crud_instance = role, crud
                    break

            # If no existing user found
            if not user:
                # Assign default role
                user_role = DEFAULT_ROLE

                # Get CRUD instance for default role
                crud_instance = ROLE_TABLES[user_role]

                # Prepare user data for creation
                user_data = {
                    "name": name,
                    "email": email,
                    "is_verified": True  # Auto-verify OAuth2 users
                }

                # Create new user record
                user = await crud_instance.create(db, user_data)

            # Generate access and refresh tokens concurrently
            access_token, refresh_token = await asyncio.gather(
                jwt_service.create_access_token(email, user_role),
                jwt_service.create_refresh_token(email, user_role)
            )

            # Get token CRUD for user role
            token_crud = TOKEN_TABLES[user_role]

            # Prepare token data for insertion
            token_data = {
                "email": email,
                "access_token": access_token,
                "refresh_token": refresh_token
            }

            # Insert new row (no overwrite) for multi-device support
            await token_crud.create(db, token_data)

            # Return dictionary containing tokens
            return {"access_token": access_token, "refresh_token": refresh_token}

        except Exception:
            # Log error with traceback and return None on failure
            logger.error("Error in login or create user:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
# Singleton instance of OAuth2Service for external use
oauth2_service = OAuth2Service()
