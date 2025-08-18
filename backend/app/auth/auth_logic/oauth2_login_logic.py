# ---------------------------- External Imports ----------------------------
# For logging and handling exceptions
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# OAuth service that handles login via third-party providers
from ..auth_services.oauth_service import oauth_service

# Rate limiter service to prevent abuse
from ..auth_security.rate_limiter_service import rate_limiter_service

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- OAuth2 Login Logic Function ----------------------------
async def handle_oauth2_login(query_params, ip_address: str):
    """
    Handle OAuth2 login flow with rate limiting.

    Parameters:
    - query_params: Query parameters from OAuth2 provider (e.g., code, state)
    - ip_address: Client IP address for rate limiting

    Returns:
    - tuple: (response_dict, status_code)
      - If successful, returns JWT tokens and 200.
      - If rate limit exceeded, returns error message and 429.
      - If login fails, returns error and 400.
      - On exception, returns error and 500.
    """
    try:
        # ---------------------------- Rate Limiting ----------------------------
        # Limit requests per IP to avoid abuse
        rate_key = f"oauth2:ip:{ip_address}"
        allowed = await rate_limiter_service.record_request(rate_key)
        if not allowed:
            return {"error": "Too many OAuth2 login attempts. Try later."}, 429

        # ---------------------------- Call OAuth Service ----------------------------
        # Handles user creation if not exists and returns JWT tokens
        user_tokens = await oauth_service.login_or_create_user(query_params)

        if not user_tokens:
            return {"error": "OAuth2 login failed"}, 400

        # OAuth2 login successful
        return user_tokens, 200

    except Exception:
        # Catch unexpected errors and log
        logger.error("Error during OAuth2 login logic:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500
