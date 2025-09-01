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

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- Login Handler Class ----------------------------
# Class responsible for handling user login requests
class LoginHandler:
    """
    Handles user login including:
    - Input validation
    - Calling login service
    - Rate limiting & lockout checks
    - Setting JWT tokens in cookies
    """

    # ---------------------------- Static Async Method ----------------------------
    # Static method to handle login without requiring class instantiation
    @staticmethod
    async def handle_login(email: str, password: str, db: AsyncSession = None):
        """
        Process login request and return JSONResponse with tokens or errors.

        Parameters:
        - email: User email
        - password: User password
        - db: Async DB session

        Returns:
        - JSONResponse with appropriate status code
        """
        try:
            # ---------------------------- Input Validation ----------------------------
            # Check if both email and password are provided
            if not email or not password:
                return JSONResponse(content={"error": "Email and password are required"}, status_code=400)

            # ---------------------------- Call Auth Service ----------------------------
            # Attempt to login using the login service
            tokens = await login_service.login(email=email, password=password, db=db)
            
            # Return error if login fails
            if not tokens:
                return JSONResponse(content={"error": "Invalid credentials or account locked"}, status_code=401)

            # ---------------------------- Login Protection ----------------------------
            # Create a unique key for tracking login attempts
            email_lock_key = f"login_lock:email:{email}"
            
            # Check if login is allowed and record the successful attempt
            allowed = await login_protection_service.check_and_record_action(email_lock_key, success=True)
            
            # If too many failed attempts, block login
            if not allowed:
                return JSONResponse(content={"error": "Too many failed login attempts, account temporarily locked"}, status_code=429)

            # ---------------------------- Set Tokens in HTTP-only Cookies ----------------------------
            # Create JSON response with login tokens
            response = JSONResponse(content=tokens, status_code=200)
            
            # Set access token cookie
            response.set_cookie(
                key="access_token",
                value=tokens["access_token"],
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=3600
            )
            
            # Set refresh token cookie
            response.set_cookie(
                key="refresh_token",
                value=tokens["refresh_token"],
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=2592000
            )

            # Return the response with tokens set
            return response

        except Exception:
            # Log the error with stack trace
            logger.error("Error during login:\n%s", traceback.format_exc())
            # Return generic server error response
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)

# ---------------------------- Instantiate LoginHandler ----------------------------
# Create a global instance of LoginHandler for usage in routes
login_handler = LoginHandler()
