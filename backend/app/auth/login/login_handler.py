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
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- Login Handler Class ----------------------------
class LoginHandler:

    # ---------------------------- Handle Login ----------------------------
    @staticmethod
    async def handle_login(email: str, password: str, db: AsyncSession = None):
        
        # Start a try-except block to handle runtime errors
        try:
            # ---------------------------- Input Validation ----------------------------
            # Check if email or password is missing
            if not email or not password:
                # Return a JSON error response if required fields are missing
                return JSONResponse(
                    content={"error": "Email and password are required"},
                    status_code=400,
                )

            # ---------------------------- Call Auth Service ----------------------------
            # Call the login service to authenticate the user
            tokens = await login_service.login(email=email, password=password, db=db)

            # If authentication fails or tokens not returned
            if not tokens:
                # Return a JSON error response for invalid credentials
                return JSONResponse(
                    content={"error": "Invalid credentials or account locked"},
                    status_code=401,
                )

            # ---------------------------- Login Protection ----------------------------
            # Create a unique key for tracking login attempts for this email
            email_lock_key = f"login_lock:email:{email}"

            # Record the successful login attempt and check if further actions are allowed
            allowed = await login_protection_service.check_and_record_action(
                email_lock_key, success=True
            )

            # If login attempts are not allowed (too many failed attempts)
            if not allowed:
                # Return a JSON error response for rate limiting / lockout
                return JSONResponse(
                    content={
                        "error": "Too many failed login attempts, account temporarily locked"
                    },
                    status_code=429,
                )

            # ---------------------------- Set Tokens in HTTP-only Cookies ----------------------------
            # Set authentication tokens in secure HTTP-only cookies and return response
            return token_cookie_handler.set_tokens_in_cookies(tokens)

        # Handle unexpected exceptions
        except Exception:
            # Log the error with traceback for debugging
            logger.error("Error during login:\n%s", traceback.format_exc())
            # Return a generic internal server error response
            return JSONResponse(
                content={"error": "Internal Server Error"}, status_code=500
            )


# ---------------------------- Instantiate LoginHandler ----------------------------
# Create a single instance of LoginHandler to be reused
login_handler = LoginHandler()
