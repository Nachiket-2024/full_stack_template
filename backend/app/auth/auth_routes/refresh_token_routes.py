# ---------------------------- External Imports ----------------------------
# FastAPI router and request handling
from fastapi import APIRouter, HTTPException, Body, Request

# For async logging and traceback
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Refresh token service to rotate tokens
from ..auth_services.refresh_token_service import refresh_token_service

# Rate limiter to prevent abuse
from ..auth_security.rate_limiter_service import rate_limiter_service

# Login protection service for failed attempts
from ..auth_security.login_protection_service import login_protection_service

# Schemas for request/response validation
from ..auth_schemas.refresh_token_schema import (
    RefreshTokenSchema,
    TokenPairResponseSchema,  # Unified schema for returning tokens
)

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Router ----------------------------
router = APIRouter(prefix="/auth/refresh", tags=["Refresh Token"])

# ---------------------------- Refresh Tokens Endpoint ----------------------------
@router.post("/", response_model=TokenPairResponseSchema)
async def refresh_tokens(request: Request, payload: RefreshTokenSchema = Body(...)):
    """
    Rotate refresh token and issue new access + refresh tokens.

    Workflow:
    - Validate the refresh token from request body
    - Apply rate limiting by client IP
    - Check login protection for repeated failed attempts
    - Call refresh token service to rotate (revoke old, issue new)
    - Record failed attempts if invalid
    - Reset failed attempts if successful
    - Return both access + refresh tokens if valid
    - Raise 401 if refresh token is invalid or revoked
    - Raise 429 if too many attempts
    """
    try:
        client_ip = request.client.host
        rate_key = f"refresh:ip:{client_ip}"
        lock_key = f"refresh:ip:{client_ip}"

        # ---------------------------- Rate Limiting ----------------------------
        if not await rate_limiter_service.record_request(rate_key):
            raise HTTPException(
                status_code=429,
                detail="Too many refresh attempts. Try again later."
            )

        # ---------------------------- Login Protection Check ----------------------------
        if await login_protection_service.is_locked(lock_key):
            raise HTTPException(
                status_code=429,
                detail="Too many failed refresh attempts. Try later."
            )

        # ---------------------------- Call Refresh Token Service ----------------------------
        tokens = await refresh_token_service.refresh_tokens(payload.refresh_token)

        # ---------------------------- Handle Invalid Token ----------------------------
        if not tokens:
            # Record the failed attempt
            await login_protection_service.record_failed_attempt(lock_key)
            raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

        # ---------------------------- Successful Refresh ----------------------------
        await login_protection_service.reset_failed_attempts(lock_key)
        return tokens

    except Exception:
        # ---------------------------- Error Logging ----------------------------
        logger.error("Error in refresh tokens endpoint:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")
