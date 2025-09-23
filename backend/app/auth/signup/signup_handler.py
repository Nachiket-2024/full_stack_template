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
# Auth service that handles user creation, password hashing, and role assignment
from .signup_service import signup_service

# Account verification service that handles email verification & Redis token management
from ..verify_account.account_verification_service import account_verification_service

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
    async def handle_signup(name: str, email: str, password: str, db: AsyncSession = None):
        """
        Input:
            1. name (str): Full name of the user.
            2. email (str): Email address of the user.
            3. password (str): Plaintext password.
            4. db (AsyncSession): Database session for creating user.

        Process:
            1. Validate required input fields (name, email, password).
            2. Call signup service to create the user in the database.
            3. Check if user creation was successful; return error if not.
            4. Send verification email using account verification service.
            5. Log warning if email sending fails.
            6. Return success JSONResponse if all steps succeed.

        Output:
            1. JSONResponse: Success or error message with appropriate HTTP status code.
        """
        try:
            # Step 1: Validate required input fields (name, email, password)
            if not name or not email or not password:
                return JSONResponse(
                    content={"error": "Name, email, and password are required"},
                    status_code=400
                )

            # Step 2: Call signup service to create the user in the database
            user_created = await signup_service.signup(
                name=name,
                email=email,
                password=password,
                db=db
            )

            # Step 3: Check if user creation was successful; return error if not
            if not user_created:
                return JSONResponse(
                    content={"error": "Signup failed (invalid data or email already registered)"},
                    status_code=400
                )

            # Step 4: Send verification email using account verification service
            email_sent = await account_verification_service.send_verification_email(email)

            # Step 5: Log warning if email sending fails
            if not email_sent:
                logger.warning("Verification email could not be sent to %s", email)

            # Step 6: Return success JSONResponse if all steps succeed
            return JSONResponse(
                content={"message": "Signup successful. Please verify your email to activate your account."},
                status_code=200
            )

        except Exception:
            # Log full exception stack trace
            logger.error("Error during signup logic:\n%s", traceback.format_exc())

            # Return generic internal server error
            return JSONResponse(
                content={"error": "Internal Server Error"},
                status_code=500
            )


# ---------------------------- Instantiate SignupHandler ----------------------------
# Singleton instance to handle signup requests
signup_handler = SignupHandler()
