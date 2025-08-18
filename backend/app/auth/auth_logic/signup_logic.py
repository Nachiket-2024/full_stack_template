# ---------------------------- External Imports ----------------------------
# For logging and handling exceptions
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Auth service that handles actual signup (hash password, create user, JWT)
from ..auth_services.auth_service import auth_service

# Rate limiter service to prevent excessive signup attempts per IP
from ..auth_security.rate_limiter_service import rate_limiter_service

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Signup Logic Function ----------------------------
async def handle_signup(name: str, email: str, password: str, ip_address: str):
    """
    Handle user signup with rate limiting.

    Parameters:
    - name: User's full name
    - email: User's email address
    - password: Plain-text password
    - ip_address: Client IP address for rate limiting

    Returns:
    - tuple: (response_dict, status_code)
      - If successful, returns JWT tokens and 200.
      - If rate limit exceeded, returns error message and 429.
      - If signup fails (existing email), returns error and 400.
      - On exception, returns error and 500.
    """
    try:
        # ---------------------------- Rate Limiting ----------------------------
        # Create a unique key per IP
        rate_key = f"signup:{ip_address}"

        # Record request and check if within allowed limit
        if not await rate_limiter_service.record_request(rate_key):
            # Return error if rate limit exceeded
            return {"error": "Too many signup attempts. Try later."}, 429

        # ---------------------------- Call Auth Service ----------------------------
        # This performs password hashing, user creation, and returns JWT tokens
        tokens = await auth_service.signup(name, email, password)

        if not tokens:
            # Signup failed (user already exists)
            return {"error": "Signup failed or email already exists"}, 400

        # Signup successful
        return tokens, 200

    except Exception:
        # Catch any unexpected errors and log for debugging
        logger.error("Error during signup logic:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500
