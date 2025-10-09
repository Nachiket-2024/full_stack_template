# ---------------------------- External Imports ----------------------------
# Capture full stack traces in case of exceptions
import traceback

# Async utilities for concurrent execution
import asyncio

# ---------------------------- Internal Imports ----------------------------
# Role tables for user CRUD operations
from ...access_control.role_tables import ROLE_TABLES

# Password service for verifying password hashes
from ..password_logic.password_service import password_service

# JWT service for creating access and refresh tokens
from ..token_logic.jwt_service import jwt_service

# Schema for structured JWT token responses
from ..token_logic.token_schema import TokenPairResponseSchema

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Login Service ----------------------------
# Service class to handle login functionality
class LoginService:
    """
    1. login - Authenticate user, verify credentials, and return access and refresh tokens.
    """

    # ---------------------------- Static Async Login Method ----------------------------
    @staticmethod
    async def login(email: str, password: str, db=None) -> TokenPairResponseSchema | None:
        """
        Input:
            1. email (str): User's email address.
            2. password (str): User's password.
            3. db: Optional database session for querying user records.

        Process:
            1. Validate that email and password are provided.
            2. Iterate through ROLE_TABLES to find the user by email.
            3. Handle case where user is not found.
            4. Ensure user account is verified.
            5. Check password correctness using password_service.
            6. Generate access and refresh tokens concurrently.
            7. Return structured token response.

        Output:
            1. TokenPairResponseSchema: Contains access_token and refresh_token if successful,
                                        otherwise returns None.
        """
        try:
            # Step 1: Validate that email and password are provided
            if not email or not password:
                return None

            # Step 2: Iterate through ROLE_TABLES to find the user by email
            user = None
            user_table_name = None
            for table_name, crud in ROLE_TABLES.items():
                user = await crud.get_by_email(email, db)
                if user:
                    user_table_name = table_name
                    break

            # Step 3: Handle case where user is not found
            if not user:
                logger.info("Login attempt with non-existing email: %s", email)
                return None

            # Step 4: Ensure user account is verified
            if not user.is_verified:
                logger.info("Login blocked for unverified account: %s", email)
                return None

            # Step 5: Check password correctness using password_service
            if not await password_service.verify_password(password, user.hashed_password):
                logger.warning("Incorrect password for email: %s", email)
                return None

            # Step 6: Generate access and refresh tokens concurrently
            access_token, refresh_token = await asyncio.gather(
                jwt_service.create_access_token(email=email ,role=user_table_name),
                jwt_service.create_refresh_token(email=email, role=user_table_name)
            )

            # Step 7: Return structured token response
            return TokenPairResponseSchema(access_token=access_token, refresh_token=refresh_token)

        except Exception:
            # Handle unexpected exceptions and log errors
            logger.error("Error during login:\n%s", traceback.format_exc())
            return None


# ---------------------------- Instantiate LoginService ----------------------------
# Singleton instance for login operations
login_service = LoginService()
