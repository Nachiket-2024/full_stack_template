# ---------------------------- External Imports ----------------------------
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

# Pydantic schema representing a pair of JWT tokens (access + refresh)
from ..token_logic.token_schema import TokenPairResponseSchema

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Login Handler Class ----------------------------
# Handler class for managing user login operations
class LoginHandler:
    """
    1. handle_login - Validates input, authenticates user, applies login protection, 
       and sets JWT cookies.
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
            2. Return error if input validation fails.
            3. Authenticate user using login_service.
            4. Return error if authentication fails.
            5. Apply login protection checks (rate-limiting, lockouts).
            6. Return error if login is temporarily locked.
            7. Set JWT tokens in HTTP-only cookies if authentication succeeds.

        Output:
            1. JSONResponse: User is either logged in with tokens set in cookies,
                             or receives an error message.
        """
        try:
            # Step 1: Validate that email and password are provided
            if not email or not password:
                # Step 2: Return error if input validation fails
                return JSONResponse(
                    content={"error": "Email and password are required"},
                    status_code=400,
                )

            # Step 3: Authenticate user using login_service
            # Returns a TokenPairResponseSchema instance if successful
            tokens: TokenPairResponseSchema = await login_service.login(
                email=email, password=password, db=db
            )

            # Step 4: Return error if authentication fails
            if not tokens:
                return JSONResponse(
                    content={"error": "Invalid credentials or account locked"},
                    status_code=401,
                )

            # Step 5: Apply login protection checks (rate-limiting, lockouts)
            email_lock_key = f"login_lock:email:{email}"
            allowed = await login_protection_service.check_and_record_action(
                email_lock_key, success=True
            )

            # Step 6: Return error if login is temporarily locked
            if not allowed:
                return JSONResponse(
                    content={
                        "error": "Too many failed login attempts, account temporarily locked"
                    },
                    status_code=429,
                )

            # Step 7: Set JWT tokens in HTTP-only cookies if authentication succeeds
            response = JSONResponse(content={"message": "Login successful"})
            # Pass the schema directly to cookie handler
            return token_cookie_handler.set_tokens_in_cookies(response, tokens)

        except Exception:
            # Handle unexpected exceptions and log errors
            logger.error("Error during login:\n%s", traceback.format_exc())

            # Return internal server error response on exception
            return JSONResponse(
                content={"error": "Internal Server Error"}, status_code=500
            )


# ---------------------------- Instantiate LoginHandler ----------------------------
# Singleton instance for reuse in routes
login_handler = LoginHandler()
