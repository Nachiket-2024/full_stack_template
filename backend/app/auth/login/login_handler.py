# ---------------------------- External Imports ----------------------------
# For logging events, errors, and debugging information
import logging

# For printing detailed exception traces in case of errors
import traceback

# Async SQLAlchemy session for database operations
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI response class for sending JSON responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Service handling login logic (password verification, token issuance)
from .login_service import login_service

# Service handling login protection like rate limiting and lockouts
from ..security.login_protection_service import login_protection_service

# Cookie utility for setting tokens
from ..token_logic.token_cookie_handler import token_cookie_handler

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Login Handler Class ----------------------------
# Handler class for managing user login operations
class LoginHandler:
    """
    1. handle_login - Validates input, authenticates user, applies login protection, and sets JWT cookies.
    """

    # ---------------------------- Handle Login ----------------------------
    # Async method to authenticate user and set JWT tokens
    async def handle_login(self, email: str, password: str, db: AsyncSession = None):
        """
        Input:
            1. email (str): User's email address.
            2. password (str): User's password.
            3. db (AsyncSession, optional): Database session for authentication.

        Process:
            1. Validate that email and password are provided.
            2. Authenticate user using login_service.
            3. Apply login protection checks (rate-limiting, lockouts).
            4. Set JWT tokens in HTTP-only cookies if authentication succeeds.

        Output:
            1. JSONResponse: User is either logged in with tokens set in cookies,
                             or receives an error message.
        """
        try:
            # Return error if email or password is missing
            if not email or not password:
                return JSONResponse(
                    content={"error": "Email and password are required"},
                    status_code=400,
                )

            # Authenticate the user via login_service and get tokens
            tokens = await login_service.login(email=email, password=password, db=db)
            # Return error if authentication fails
            if not tokens:
                return JSONResponse(
                    content={"error": "Invalid credentials or account locked"},
                    status_code=401,
                )

            # Generate key for tracking login attempts for this email
            email_lock_key = f"login_lock:email:{email}"

            # Record the successful login attempt and verify if allowed
            allowed = await login_protection_service.check_and_record_action(
                email_lock_key, success=True
            )
            # Return error if too many failed attempts
            if not allowed:
                return JSONResponse(
                    content={
                        "error": "Too many failed login attempts, account temporarily locked"
                    },
                    status_code=429,
                )

            # Set authentication tokens in secure HTTP-only cookies
            return token_cookie_handler.set_tokens_in_cookies(tokens)

        # Catch all unexpected errors
        except Exception:
            # Log full traceback for debugging
            logger.error("Error during login:\n%s", traceback.format_exc())
            
            # Return generic internal server error response
            return JSONResponse(
                content={"error": "Internal Server Error"}, status_code=500
            )


# ---------------------------- Instantiate LoginHandler ----------------------------
# Singleton instance for reuse in routes
login_handler = LoginHandler()
