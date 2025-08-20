# ---------------------------- External Imports ----------------------------
# For logging and handling exceptions
import logging
import traceback
import asyncio  # For concurrent execution of async tasks

# ---------------------------- Internal Imports ----------------------------
# Auth service that handles login (password verification, JWT issuance)
from ..auth_services.auth_service import auth_service

# Rate limiter service to prevent brute-force and excessive login attempts
from ..auth_security.rate_limiter_service import rate_limiter_service

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Login Logic Function ----------------------------
async def handle_login(email: str, password: str, ip_address: str):
    """
    Handle user login with brute-force protection and rate limiting.

    Parameters:
    - email: User's email
    - password: Plain-text password
    - ip_address: Client IP address for rate limiting

    Returns:
    - tuple: (response_dict, status_code)
      - If successful, returns JWT tokens and 200.
      - If rate limit exceeded, returns error message and 429.
      - If login fails (invalid credentials), returns error and 401.
      - On exception, returns error and 500.
    """
    try:
        # ---------------------------- Input Validation ----------------------------
        if not email or not password:
            return {"error": "Email and password are required"}, 400

        # ---------------------------- Rate Limiting ----------------------------
        # Create unique keys per email and per IP for login attempts
        email_rate_key = f"login:email:{email}"
        ip_rate_key = f"login:ip:{ip_address}"

        # Run both rate-limit checks concurrently to save time
        email_allowed, ip_allowed = await asyncio.gather(
            rate_limiter_service.record_request(email_rate_key),
            rate_limiter_service.record_request(ip_rate_key)
        )
        if not email_allowed or not ip_allowed:
            return {"error": "Too many login attempts. Try later."}, 429

        # ---------------------------- Call Auth Service ----------------------------
        # Performs password verification, brute-force protection, and returns JWT tokens
        tokens = await auth_service.login(email, password, ip_address)

        if not tokens:
            # Login failed (invalid credentials or locked account)
            return {"error": "Invalid credentials or account locked"}, 401

        # ---------------------------- Login Successful ----------------------------
        return tokens, 200

    except Exception:
        # Catch unexpected errors and log full traceback
        logger.error("Error during login logic:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500
