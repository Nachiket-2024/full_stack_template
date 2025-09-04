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
    """
    1. exchange_code_for_tokens - Exchange authorization code for Google access and refresh tokens.
    2. get_user_info - Retrieve Google user profile information using access token.
    3. login_or_create_user - Authenticate existing user or create new user and generate JWT tokens.
    """

    # ---------------------------- Exchange Code for Tokens ----------------------------
    # Exchange authorization code for access and refresh tokens from Google
    @staticmethod
    async def exchange_code_for_tokens(code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict | None:
        """
        Input:
            1. code (str): Authorization code from Google.
            2. client_id (str): Google OAuth2 client ID.
            3. client_secret (str): Google OAuth2 client secret.
            4. redirect_uri (str): Callback URL.

        Process:
            1. Build payload with code, client credentials, redirect_uri, grant_type.
            2. Make async POST request to Google's token endpoint.
            3. Parse JSON response.

        Output:
            1. dict: Contains access_token, refresh_token, etc., or None on error.
        """
        try:
            # ---------------------------- Define Token Endpoint ----------------------------
            # URL for Google token exchange
            token_url = "https://oauth2.googleapis.com/token"

            # ---------------------------- Prepare POST Payload ----------------------------
            # Data to send in POST request
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }

            # ---------------------------- Make Async POST Request ----------------------------
            # Use httpx AsyncClient to send POST request
            async with httpx.AsyncClient() as client:
                resp = await client.post(token_url, data=data)  # Send request
                resp.raise_for_status()  # Raise exception for HTTP errors
                return resp.json()  # Return JSON response

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log errors with full traceback
            logger.error("Error exchanging code for tokens:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Get User Info ----------------------------
    # Retrieve user profile information from Google using access token
    @staticmethod
    async def get_user_info(access_token: str) -> dict | None:
        """
        Input:
            1. access_token (str): Google OAuth2 access token.

        Process:
            1. Build request headers with Bearer token.
            2. Make async GET request to Google userinfo endpoint.
            3. Parse JSON response.

        Output:
            1. dict: Contains user profile info (email, name, etc.) or None on error.
        """
        try:
            # ---------------------------- Define Userinfo Endpoint ----------------------------
            # Google endpoint for fetching user info
            userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}  # Add auth header

            # ---------------------------- Make Async GET Request ----------------------------
            # Use httpx AsyncClient to fetch user info
            async with httpx.AsyncClient() as client:
                resp = await client.get(userinfo_url, headers=headers)  # Send GET request
                resp.raise_for_status()  # Raise exception for HTTP errors
                return resp.json()  # Return JSON response

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log errors with full traceback
            logger.error("Error fetching user info:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Login or Create User ----------------------------
    # Authenticate existing user or create new user and generate JWT tokens
    @staticmethod
    async def login_or_create_user(db, user_info: dict) -> dict | None:
        """
        Input:
            1. db: Database session for user operations.
            2. user_info (dict): Contains user email and name from Google.

        Process:
            1. Extract email and name from user_info.
            2. Check all role tables for existing user.
            3. If user does not exist, create new with default role.
            4. Generate access and refresh JWT tokens concurrently.
            5. Update tokens in the database.

        Output:
            1. dict: Contains generated access_token and refresh_token or None on error.
        """
        try:
            # ---------------------------- Extract Email and Name ----------------------------
            # Get email and name from Google user info
            email = user_info.get("email")
            name = user_info.get("name", "Unknown")

            # ---------------------------- Initialize Variables ----------------------------
            # Initialize placeholders for user, role, and CRUD instance
            user = None
            user_role = None
            crud_instance = None

            # ---------------------------- Check Existing User ----------------------------
            # Iterate over role tables to find existing user by email
            for role, crud in ROLE_TABLES.items():
                user = await crud.get_by_email(db, email)  # Query user
                if user:
                    user_role = role  # Assign role if user exists
                    crud_instance = crud  # Assign CRUD instance
                    break  # Stop loop once user is found

            # ---------------------------- Create New User if Not Found ----------------------------
            if not user:
                user_role = DEFAULT_ROLE  # Assign default role
                crud_instance = ROLE_TABLES[user_role]  # Get CRUD for default role
                user_data = {"name": name, "email": email}  # Prepare user data
                user = await crud_instance.create(db, user_data)  # Create user

            # ---------------------------- Generate JWT Tokens ----------------------------
            # Generate access and refresh tokens concurrently
            access_token, refresh_token = await asyncio.gather(
                jwt_service.create_access_token(email, user_role),
                jwt_service.create_refresh_token(email, user_role)
            )

            # ---------------------------- Update Tokens in Database ----------------------------
            # Update user record with new tokens
            await crud_instance.update_by_email(db, email, {
                "access_token": access_token,
                "refresh_token": refresh_token
            })

            # ---------------------------- Return Tokens ----------------------------
            # Return generated tokens
            return {"access_token": access_token, "refresh_token": refresh_token}

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log exception with full traceback
            logger.error("Error in login or create user:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
# Singleton instance of OAuth2Service for reuse in handlers
oauth2_service = OAuth2Service()
