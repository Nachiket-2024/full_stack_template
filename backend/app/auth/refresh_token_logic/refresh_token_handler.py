# ---------------------------- External Imports ----------------------------
# Import FastAPI exceptions and request parsing
from fastapi import HTTPException, Request, Body

# Import Python built-in logging
import logging

# Import traceback for detailed error reporting
import traceback

# ---------------------------- Internal Imports ----------------------------
# Import service responsible for validating and rotating refresh tokens
from ...auth.refresh_token_logic.refresh_token_service import refresh_token_service

# Import service to enforce rate limiting
from ...auth.security.rate_limiter_service import rate_limiter_service

# Import service that provides brute-force protection
from ...auth.security.login_protection_service import login_protection_service

# Import schemas for request validation
from ...auth.refresh_token_logic.refresh_token_schema import RefreshTokenSchema

# Import cookie utility for setting tokens
from ...auth.token_logic.token_cookie_handler import token_cookie_handler

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- Refresh Token Handler ----------------------------
# Define handler class for refresh token operations
class RefreshTokenHandler:

    # ---------------------------- Handle Refresh Tokens ----------------------------
    # Define static method to handle refresh token logic
    @staticmethod
    async def handle_refresh_tokens(request: Request, payload: RefreshTokenSchema = Body(...)):
        # Start a try-except block to catch runtime errors
        try:
            # ---------------------------- Extract Client Info ----------------------------
            # Extract client IP address from request
            client_ip = request.client.host

            # Create Redis keys for rate limiting and login protection
            rate_key = f"refresh:ip:{client_ip}"
            lock_key = f"refresh:ip:{client_ip}"

            # ---------------------------- Rate Limiting ----------------------------
            # Check if client has exceeded allowed refresh attempts
            if not await rate_limiter_service.record_request(rate_key):
                # Raise HTTP 429 if too many requests
                raise HTTPException(
                    status_code=429,
                    detail="Too many refresh attempts. Try again later."
                )

            # ---------------------------- Login Protection Check ----------------------------
            # Check if the client IP is temporarily locked due to failed attempts
            if await login_protection_service.is_locked(lock_key):
                # Raise HTTP 429 if account is locked
                raise HTTPException(
                    status_code=429,
                    detail="Too many failed refresh attempts. Try later."
                )

            # ---------------------------- Call Refresh Token Service ----------------------------
            # Call service to validate and rotate refresh token
            tokens = await refresh_token_service.refresh_tokens(payload.refresh_token)

            # ---------------------------- Handle Invalid Token ----------------------------
            # If refresh token is invalid or revoked
            if not tokens:
                # Record failed attempt for brute-force protection
                await login_protection_service.record_failed_attempt(lock_key)
                # Raise HTTP 401 for invalid token
                raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

            # ---------------------------- Successful Refresh ----------------------------
            # Reset failed attempts counter on successful refresh
            await login_protection_service.reset_failed_attempts(lock_key)

            # ---------------------------- Set Tokens in HTTP-only Cookies ----------------------------
            # Return response with new tokens set in secure cookies
            return token_cookie_handler.set_tokens_in_cookies(tokens)

        # ---------------------------- Exception Handling ----------------------------
        # Catch unexpected exceptions
        except Exception:
            # Log error with traceback for debugging
            logger.error("Error in refresh tokens handler:\n%s", traceback.format_exc())
            # Raise generic internal server error
            raise HTTPException(status_code=500, detail="Internal Server Error")


# ---------------------------- Singleton Instance ----------------------------
# Create a reusable instance of RefreshTokenHandler
refresh_token_handler = RefreshTokenHandler()
