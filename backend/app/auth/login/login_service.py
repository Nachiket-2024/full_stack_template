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
from ..token_logic.refresh_token_schema import TokenPairResponseSchema

# ---------------------------- Logger Setup ----------------------------
# Configure logger specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Login Service ----------------------------
# Service class to handle login functionality
class LoginService:
    """
    Handles user login flow:
    - Validates email/password
    - Issues JWT tokens
    - Stores/updates tokens in dedicated token tables
    """

    # ---------------------------- Static Async Login Method ----------------------------
    # Static async method for user login
    @staticmethod
    async def login(email: str, password: str, db=None) -> TokenPairResponseSchema | None:
        """
        Handle user login.

        Parameters:
        - email: User's email
        - password: Plain-text password
        - db: AsyncSession for database operations (required for token CRUD)

        Returns:
        - TokenPairResponseSchema if successful
        - None if login fails
        """
        try:
            # ---------------------------- Input Validation ----------------------------
            # Return None if email or password is missing
            if not email or not password:
                return None

            # ---------------------------- Find User ----------------------------
            # Initialize variables
            user = None
            user_role = None

            # Iterate over all roles to find the user by email
            for role_name, crud in ROLE_TABLES.items():
                user = await crud.get_by_email(email, db=db)
                if user:
                    user_role = role_name
                    break

            # Log and return None if user is not found
            if not user:
                logger.info("Login attempt with non-existing email: %s", email)
                return None

            # ---------------------------- Check Verification ----------------------------
            # Ensure user account is verified before login
            if not getattr(user, "is_verified", False):
                logger.info("Login blocked for unverified account: %s", email)
                return None

            # ---------------------------- Verify Password ----------------------------
            # Check if the provided password matches the stored hash
            if not await password_service.verify_password(password, user.hashed_password):
                logger.warning("Incorrect password for email: %s", email)
                return None

            # ---------------------------- Generate Tokens ----------------------------
            # Concurrently create access and refresh tokens
            access_token, refresh_token = await asyncio.gather(
                jwt_service.create_access_token(email, user_role),
                jwt_service.create_refresh_token(email, user_role)
            )

            # ---------------------------- Update or Create Token Record ----------------------------
            # Get token CRUD operations for the user role
            token_crud = TOKEN_TABLES[user_role]
            
            # Check if token already exists
            existing_token = await token_crud.get_by_access_token(db, access_token)
            
            # Update refresh token if access token exists
            if existing_token:
                await token_crud.update_refresh_token_by_access_token(db, access_token, refresh_token)
            else:
                # Create new token record if none exists
                token_data = {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
                await token_crud.create(db, token_data)

            # ---------------------------- Return Tokens ----------------------------
            # Return structured token response
            return TokenPairResponseSchema(access_token=access_token, refresh_token=refresh_token)

        except Exception:
            # Log full exception stack trace
            logger.error("Error during login:\n%s", traceback.format_exc())
            return None


# ---------------------------- Instantiate LoginService ----------------------------
# Singleton instance for login operations
login_service = LoginService()
