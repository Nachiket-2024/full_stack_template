# ---------------------------- External Imports ----------------------------
# For logging and handling exceptions
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Auth service that handles actual signup (hash password, create user, JWT)
from ..auth_services.auth_service import auth_service

# Rate limiter service to prevent excessive signup attempts per IP
from ..auth_security.rate_limiter_service import rate_limiter_service

# Account verification service (handles token generation & Redis)
from ..auth_services.account_verification_service import account_verification_service

# Default role is set in role_tables file
from ...core.role_tables import DEFAULT_ROLE

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Signup Logic Function ----------------------------
async def handle_signup(name: str, email: str, password: str, ip_address: str, role: str = DEFAULT_ROLE):
    """
    Handle user signup with:
    1. Rate limiting
    2. User creation (is_verified=False)
    3. Verification email via Celery & Redis token

    Public signup always uses default role. Admin routes can specify other roles.

    Parameters:
    - name: User's full name
    - email: User's email address
    - password: Plain-text password
    - ip_address: Client IP address for rate limiting
    - role: Role for the user (default role)

    Returns:
    - tuple: (response_dict, status_code)
    """
    try:
        # ---------------------------- Rate Limiting ----------------------------
        rate_key = f"signup:{ip_address}"
        if not await rate_limiter_service.record_request(rate_key):
            return {"error": "Too many signup attempts. Try later."}, 429

        # ---------------------------- Force Default Role for Public Signup ----------------------------
        role = DEFAULT_ROLE  # public signup always Default Role

        # ---------------------------- Call Auth Service ----------------------------
        user_created = await auth_service.signup(
            name=name,
            email=email,
            password=password,
            role=role
        )

        if not user_created:
            return {"error": "Signup failed or email already exists"}, 400

        # ---------------------------- Send Verification Email ----------------------------
        email_sent = await account_verification_service.send_verification_email(email, role)
        if not email_sent:
            logger.warning("Failed to send verification email for %s", email)

        # ---------------------------- Response ----------------------------
        return {
            "message": "Signup successful. Please verify your email to activate your account."
        }, 200

    except Exception:
        logger.error("Error during signup logic:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500
