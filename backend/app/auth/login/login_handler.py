# ---------------------------- External Imports ----------------------------
# For logging events, errors, and debugging information
import logging

# For printing detailed exception traces in case of errors
import traceback

# Async SQLAlchemy session for database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Auth service that handles login logic (password verification, JWT issuance)
from .login_service import login_service

# ---------------------------- Logger Setup ----------------------------
# Configure logger instance specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Login Handler Class ----------------------------
# Class to encapsulate login handling logic
class LoginHandler:
    """
    Handles user login:
    - Validates inputs
    - Calls LoginService for authentication
    - Returns tokens or error responses
    """

    # ---------------------------- Static Async Method ----------------------------
    # Static async method to process login requests
    @staticmethod
    async def handle_login(email: str, password: str, db: AsyncSession = None):
        """
        Handle user login.

        Parameters:
        - email: User's email
        - password: Plain-text password
        - db: Async DB session for user lookup

        Returns:
        - tuple: (response_dict, status_code)
          - If successful, returns JWT tokens and 200.
          - If login fails (invalid credentials), returns error and 401.
          - On exception, returns error and 500.
        """
        try:
            # ---------------------------- Input Validation ----------------------------
            # Return error if email or password is missing
            if not email or not password:
                return {"error": "Email and password are required"}, 400

            # ---------------------------- Call Auth Service ----------------------------
            # Use the login service to validate credentials and get JWT tokens
            tokens = await login_service.login(email=email, password=password, db=db)

            # If authentication fails, return error response
            if not tokens:
                return {"error": "Invalid credentials or account locked"}, 401

            # ---------------------------- Login Successful ----------------------------
            # Return token response with success status code
            return tokens, 200

        except Exception:
            # Log full exception stack trace for debugging
            logger.error("Error during login logic:\n%s", traceback.format_exc())
            
            # Return generic internal server error
            return {"error": "Internal Server Error"}, 500


# ---------------------------- Instantiate LoginHandler ----------------------------
# Singleton instance for handling login requests
login_handler = LoginHandler()
