# ---------------------------- External Imports ----------------------------
# Logging for structured event and error logging
import logging

# Capture full stack traces in case of exceptions
import traceback

# Async utilities for concurrent execution
import asyncio

# ---------------------------- Internal Imports ----------------------------
# Role tables for user CRUD operations
from ...access_control.role_tables import ROLE_TABLES, TOKEN_TABLES

# Password service for verifying password hashes
from ..password_logic.password_service import password_service

# JWT service for creating access and refresh tokens
from ..token_logic.jwt_service import jwt_service

# Schema for structured JWT token responses
from ..refresh_token_logic.refresh_token_schema import TokenPairResponseSchema

# ---------------------------- Logger Setup ----------------------------
# Configure logger specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Login Service ----------------------------
# Service class to handle login functionality
class LoginService:
    """
    1. login - Authenticate user, verify credentials, and return access and refresh tokens.
    """

    # ---------------------------- Static Async Login Method ----------------------------
    # Static async method for user login
    @staticmethod
    async def login(email: str, password: str, db=None) -> TokenPairResponseSchema | None:
        """
        Input:
            1. email (str): User's email address.
            2. password (str): User's password.
            3. db: Optional database session for querying user and token records.

        Process:
            1. Validate that email and password are provided.
            2. Iterate through ROLE_TABLES to find the user by email.
            3. Verify that the user account is verified.
            4. Check password correctness using password_service.
            5. Generate access and refresh tokens concurrently.
            6. Update or create token record in TOKEN_TABLES.
            7. Return structured token response.

        Output:
            1. TokenPairResponseSchema: Contains access_token and refresh_token if successful,
                                        otherwise returns None.
        """
        try:
            # Return None if email or password is missing
            if not email or not password:
                return None

            # Initialize variables
            user = None
            user_table_name = None

            # Iterate over all role tables to find the user by email
            for table_name, crud in ROLE_TABLES.items():
                user = await crud.get_by_email(db, email)  # returns correct model instance
                if user:
                    user_table_name = table_name
                    break

            # Log and return None if user is not found
            if not user:
                logger.info("Login attempt with non-existing email: %s", email)
                return None

            # Ensure user account is verified before login
            if not user.is_verified:
                logger.info("Login blocked for unverified account: %s", email)
                return None

            # Check if the provided password matches the stored hash
            if not await password_service.verify_password(password, user.hashed_password):
                logger.warning("Incorrect password for email: %s", email)
                return None

            # Concurrently create access and refresh tokens
            access_token, refresh_token = await asyncio.gather(
                jwt_service.create_access_token(email, user_table_name),
                jwt_service.create_refresh_token(email, user_table_name)
            )

            # Get token CRUD instance for the user's role/table
            token_crud = TOKEN_TABLES[user_table_name]

            # Check if token already exists (by access token)
            existing_token = await token_crud.get_by_access_token(db, access_token)

            # Update refresh token if access token exists
            if existing_token:
                await token_crud.update_refresh_token_by_access_token(db, access_token, refresh_token)
            else:
                # Create new token record if none exists, including email for FK
                token_data = {
                    "email": email,  # FK mapping
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
                await token_crud.create(db, token_data)

            # Return structured token response
            return TokenPairResponseSchema(access_token=access_token, refresh_token=refresh_token)

        # Catch all unexpected errors
        except Exception:
            # Log full exception stack trace
            logger.error("Error during login:\n%s", traceback.format_exc())
            return None


# ---------------------------- Instantiate LoginService ----------------------------
# Singleton instance for login operations
login_service = LoginService()
