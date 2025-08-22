# ---------------------------- External Imports ----------------------------
# Logging for tracking events, warnings, and errors
import logging

# Capture full stack traces for detailed exception debugging
import traceback

# Async SQLAlchemy session for database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Auth service that handles user creation and password hashing (no JWT here)
from .signup_service import signup_service

# Account verification service that handles email verification & Redis token management
from ..verify_account.account_verification_service import account_verification_service

# Default role to assign to new users if role not specified
from ...access_control.role_tables import DEFAULT_ROLE

# ---------------------------- Logger Setup ----------------------------
# Configure module-specific logger (centralized config recommended in production)
logger = logging.getLogger(__name__)

# ---------------------------- Signup Handler Class ----------------------------
# Class encapsulating user signup logic
class SignupHandler:
    """
    Handles user signup:
    1. Calls SignupService to create user (is_verified=False initially)
    2. Sends account verification email
    """

    # ---------------------------- Static Async Signup Method ----------------------------
    # Static async method for handling signup requests
    @staticmethod
    async def handle_signup(name: str, email: str, password: str, role: str = DEFAULT_ROLE, db: AsyncSession = None):
        try:
            # Always assign default role (overwrites input role for now)
            role = DEFAULT_ROLE

            # Call signup service to create user in the database
            user_created = await signup_service.signup(
                name=name,
                email=email,
                password=password,
                role=role,
                db=db
            )

            # Return error if user creation fails (invalid input or duplicate email)
            if not user_created:
                return {"error": "Signup failed (invalid data or email already registered)"}, 400

            # ---------------------------- Send Verification Email ----------------------------
            # Trigger sending of verification email for newly created user
            email_sent = await account_verification_service.send_verification_email(email, role)
            
            # Log warning if email sending fails but continue flow
            if not email_sent:
                logger.warning("Verification email could not be sent to %s", email)

            # Return success response
            return {"message": "Signup successful. Please verify your email to activate your account."}, 200

        except Exception:
            # Log full exception stack trace for debugging
            logger.error("Error during signup logic:\n%s", traceback.format_exc())
            
            # Return generic internal server error
            return {"error": "Internal Server Error"}, 500


# ---------------------------- Instantiate SignupHandler ----------------------------
# Singleton instance to handle signup requests
signup_handler = SignupHandler()
