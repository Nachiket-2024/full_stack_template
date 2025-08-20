# ---------------------------- External Imports ----------------------------
# For logging and handling exceptions
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# OAuth service for code-to-token exchange and user info
from ..auth_services.oauth_service import oauth_service

# Rate limiter service to prevent abuse
from ..auth_security.rate_limiter_service import rate_limiter_service

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- OAuth2 Login Logic Function ----------------------------
async def handle_oauth2_login(query_params: dict, ip_address: str):
    """
    Handle Google OAuth2 redirect flow:
    1. Rate-limiting by IP
    2. Exchange authorization code for access token
    3. Get user info from Google
    4. Login or create user in DB
    5. Return JWT tokens for frontend redirect

    Parameters:
    - query_params: Query parameters from OAuth2 callback (e.g., code)
    - ip_address: Client IP address for rate limiting

    Returns:
    - tuple: (jwt_tokens_dict, status_code)
    """
    try:
        # ---------------------------- Rate Limiting ----------------------------
        rate_key = f"oauth2:ip:{ip_address}"
        if not await rate_limiter_service.record_request(rate_key):
            # Return status 429 for too many attempts
            return {"error": "Too many OAuth2 login attempts. Try later."}, 429

        # ---------------------------- Get Authorization Code ----------------------------
        code = query_params.get("code")
        if not code:
            return {"error": "Missing authorization code"}, 400

        # ---------------------------- Exchange Code for Access Token ----------------------------
        token_data = await oauth_service.exchange_code_for_tokens(code)
        if not token_data or "access_token" not in token_data:
            return {"error": "Failed to exchange code for access token"}, 400

        access_token_google = token_data["access_token"]

        # ---------------------------- Fetch User Info from Google ----------------------------
        user_info = await oauth_service.get_user_info(access_token_google)
        if not user_info or "email" not in user_info:
            return {"error": "Failed to fetch user info from Google"}, 400

        # ---------------------------- Login or Create User ----------------------------
        jwt_tokens = await oauth_service.login_or_create_user(user_info)
        if not jwt_tokens:
            return {"error": "Failed to login or create user"}, 500

        # ---------------------------- Return JWT Tokens for Redirect ----------------------------
        # The caller (callback route) will handle redirect with these tokens
        return jwt_tokens, 200

    except Exception:
        logger.error("Error during OAuth2 login logic:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500
