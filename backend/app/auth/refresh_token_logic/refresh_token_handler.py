# ---------------------------- External Imports ----------------------------
# Import FastAPI classes for exceptions, request parsing, and dependency injection
from fastapi import HTTPException, Request, Body

# Import traceback to capture detailed stack traces for debugging
import traceback

# Import FastAPI's JSONResponse for constructing responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Import service responsible for validating and rotating refresh tokens
from ...auth.refresh_token_logic.refresh_token_service import refresh_token_service

# Import service to enforce rate limiting
from ...auth.security.rate_limiter_service import rate_limiter_service

# Import service that provides brute-force protection
from ...auth.security.login_protection_service import login_protection_service

# Import Pydantic schema representing the refresh token request payload
from ..token_logic.token_schema import RefreshTokenSchema

# Import Pydantic schema representing a pair of JWT tokens (access + refresh)
from ..token_logic.token_schema import TokenPairResponseSchema

# Import cookie handler to securely set tokens in HTTP-only cookies
from ..token_logic.token_cookie_handler import token_cookie_handler

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Refresh Token Handler Class ----------------------------
# Handler class responsible for validating, rotating, and setting new refresh tokens securely
class RefreshTokenHandler:
    """
    1. handle_refresh_tokens - Validate and rotate refresh tokens with rate limiting and brute-force protection.
    """

    # ---------------------------- Handle Refresh Tokens ----------------------------
    # Static method to process refresh token rotation requests
    @staticmethod
    async def handle_refresh_tokens(request: Request, payload: RefreshTokenSchema = Body(...)):
        """
        Input:
            1. request (Request): FastAPI request object containing client connection metadata.
            2. payload (RefreshTokenSchema): Request body containing the user's refresh token.

        Process:
            1. Extract client IP address from request.
            2. Generate Redis keys for rate limiting and brute-force tracking.
            3. Enforce rate limit to prevent abuse.
            4. Check if client IP is locked due to repeated failed attempts.
            5. Validate and rotate refresh token using refresh_token_service.
            6. Handle invalid or revoked refresh tokens and record failure.
            7. Reset failed attempt counter on successful token rotation.
            8. Create a response object to attach new tokens.
            9. Attach access and refresh tokens as secure HTTP-only cookies.
            10. Return the final response object with cookies set.

        Output:
            1. JSONResponse: Response with cookies set or raises HTTPException on validation or server errors.
        """
        try:
            # Step 1: Extract client IP address from request
            client_ip = request.client.host

            # Step 2: Generate Redis keys for rate limiting and brute-force tracking
            rate_key = f"refresh:ip:{client_ip}"
            lock_key = f"refresh:ip:{client_ip}"

            # Step 3: Enforce rate limit to prevent abuse
            allowed = await rate_limiter_service.record_request(rate_key)
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail="Too many refresh attempts. Try again later."
                )

            # Step 4: Check if client IP is locked due to repeated failed attempts
            is_locked = await login_protection_service.is_locked(lock_key)
            if is_locked:
                raise HTTPException(
                    status_code=429,
                    detail="Too many failed refresh attempts. Try later."
                )

            # Step 5: Validate and rotate refresh token using refresh_token_service
            tokens: TokenPairResponseSchema = await refresh_token_service.refresh_tokens(payload.refresh_token)

            # Step 6: Handle invalid or revoked refresh tokens and record failure
            if not tokens or not tokens.access_token:
                await login_protection_service.record_failed_attempt(lock_key)
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or revoked refresh token"
                )

            # Step 7: Reset failed attempt counter on successful token rotation
            await login_protection_service.reset_failed_attempts(lock_key)

            # Step 8: Create a response object to attach new tokens
            response = JSONResponse(content={"message": "Tokens refreshed successfully"})

            # Step 9: Attach access and refresh tokens as secure HTTP-only cookies
            token_cookie_handler.set_tokens_in_cookies(response, tokens)

            # Step 10: Return the final response object with cookies set
            return response

        except HTTPException:
            # Re-raise controlled HTTP exceptions (client errors)
            raise

        except Exception:
            # Handle and log unexpected errors gracefully
            logger.error("Error in refresh token handler:\n%s", traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal Server Error")


# ---------------------------- Singleton Instance ----------------------------
# Single global instance of RefreshTokenHandler for consistent refresh logic across routes
refresh_token_handler = RefreshTokenHandler()
