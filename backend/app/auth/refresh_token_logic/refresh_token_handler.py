# ---------------------------- External Imports ----------------------------
# Import FastAPI exceptions and request parsing
from fastapi import HTTPException, Request, Body

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

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Refresh Token Handler Class ----------------------------
# Handler class responsible for refresh token operations
class RefreshTokenHandler:
    """
    1. handle_refresh_tokens - Validate and rotate refresh tokens with rate limiting and brute-force protection.
    """

    # ---------------------------- Handle Refresh Tokens ----------------------------
    # Static method to process refresh token requests
    @staticmethod
    async def handle_refresh_tokens(request: Request, payload: RefreshTokenSchema = Body(...)):
        """
        Input:
            1. request (Request): FastAPI request object for client information.
            2. payload (RefreshTokenSchema): Request body containing refresh token.

        Process:
            1. Extract client IP address and generate Redis keys for rate limiting and lockout.
            2. Check rate limits for the IP address.
            3. Verify if the IP is temporarily locked due to failed attempts.
            4. Validate and rotate the refresh token using refresh_token_service.
            5. Handle invalid or revoked tokens and record failed attempts.
            6. Reset failed attempts counter on successful refresh.
            7. Set new access and refresh tokens in secure HTTP-only cookies and return it.

        Output:
            1. Response object with cookies set or raises HTTPException on error.
        """
        try:
            # Step 1: Extract client IP address from request
            client_ip = request.client.host

            # Step 1a: Generate Redis keys for rate limiting and lockout
            rate_key = f"refresh:ip:{client_ip}"
            lock_key = f"refresh:ip:{client_ip}"

            # Step 2: Check if client has exceeded allowed refresh attempts
            if not await rate_limiter_service.record_request(rate_key):
                # Step 2a: Raise HTTP 429 if too many requests
                raise HTTPException(
                    status_code=429,
                    detail="Too many refresh attempts. Try again later."
                )

            # Step 3: Check if the client IP is temporarily locked due to failed attempts
            if await login_protection_service.is_locked(lock_key):
                # Step 3a: Raise HTTP 429 if account is locked
                raise HTTPException(
                    status_code=429,
                    detail="Too many failed refresh attempts. Try later."
                )

            # Step 4: Validate and rotate the refresh token using refresh_token_service
            tokens = await refresh_token_service.refresh_tokens(payload.refresh_token)

            # Step 5: Handle invalid or revoked tokens
            if not tokens:
                # Step 5a: Record failed attempt for brute-force protection
                await login_protection_service.record_failed_attempt(lock_key)

                # Step 5b: Raise HTTP 401 for invalid token
                raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

            # Step 6: Reset failed attempts counter on successful refresh
            await login_protection_service.reset_failed_attempts(lock_key)

            # Step 7: Set new access and refresh tokens in secure HTTP-only cookies and return it
            return token_cookie_handler.set_tokens_in_cookies(tokens)

        except Exception:
            # Handle unexpected exceptions and log errors
            logger.error("Error in refresh tokens handler:\n%s", traceback.format_exc())

            # Raise generic internal server error
            raise HTTPException(status_code=500, detail="Internal Server Error")


# ---------------------------- Singleton Instance ----------------------------
# Create a reusable instance of RefreshTokenHandler
refresh_token_handler = RefreshTokenHandler()
