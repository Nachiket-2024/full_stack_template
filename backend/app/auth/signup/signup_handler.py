# ---------------------------- External Imports ----------------------------
# Logging for tracking events, warnings, and errors
import logging

# Capture full stack traces for detailed exception debugging
import traceback

# Async SQLAlchemy session for database operations
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI response class for sending JSON responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Auth service that handles user creation and password hashing
from .signup_service import signup_service

# Account verification service that handles email verification & Redis token management
from ..verify_account.account_verification_service import account_verification_service

# Default role to assign to new users if role not specified
from ...access_control.role_tables import DEFAULT_ROLE

# ---------------------------- Logger Setup ----------------------------
# Configure module-specific logger
logger = logging.getLogger(__name__)

# ---------------------------- Signup Handler Class ----------------------------
# Class encapsulating user signup logic
class SignupHandler:
    """
    1. handle_signup - Handle user signup, create account, and send verification email.
    """

    # ---------------------------- Static Async Signup Method ----------------------------
    @staticmethod
    async def handle_signup(name: str, email: str, password: str, role: str = DEFAULT_ROLE, db: AsyncSession = None):
        """
        Input:
            1. name (str): Full name of the user.
            2. email (str): Email address of the user.
            3. password (str): Plaintext password.
            4. role (str): Role to assign (default applied).
            5. db (AsyncSession): Database session for creating user.

        Process:
            1. Validate required input fields.
            2. Assign default role to user.
            3. Call signup service to create user in DB.
            4. Send verification email using verification service.
            5. Log any issues but continue flow.

        Output:
            1. JSONResponse: Success or error message with HTTP status code.
        """
        try:
            # ---------------------------- Input Validation ----------------------------
            # Ensure required fields are provided
            if not name or not email or not password:
                # Return 400 if missing any required field
                return JSONResponse(content={"error": "Name, email, and password are required"}, status_code=400)

            # ---------------------------- Assign Role ----------------------------
            # Always assign default role (overwrites input role for now)
            role = DEFAULT_ROLE

            # ---------------------------- Call Signup Service ----------------------------
            # Create user in the database
            user_created = await signup_service.signup(
                name=name,               # User's full name
                email=email,             # User's email
                password=password,       # Plaintext password
                role=role,               # Assigned role
                db=db                    # Async database session
            )

            # Return error if user creation fails (invalid input or duplicate email)
            if not user_created:
                return JSONResponse(
                    content={"error": "Signup failed (invalid data or email already registered)"},
                    status_code=400
                )

            # ---------------------------- Send Verification Email ----------------------------
            # Trigger sending of verification email
            email_sent = await account_verification_service.send_verification_email(email, role)
            
            # Log warning if email sending fails but continue flow
            if not email_sent:
                logger.warning("Verification email could not be sent to %s", email)

            # ---------------------------- Return Success ----------------------------
            # Respond with success message and instructions
            return JSONResponse(
                content={"message": "Signup successful. Please verify your email to activate your account."},
                status_code=200
            )

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log full exception stack trace
            logger.error("Error during signup logic:\n%s", traceback.format_exc())
            
            # Return generic internal server error
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# ---------------------------- Instantiate SignupHandler ----------------------------
# Singleton instance to handle signup requests
signup_handler = SignupHandler()
