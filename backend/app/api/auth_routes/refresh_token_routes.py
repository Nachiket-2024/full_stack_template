# ---------------------------- External Imports ----------------------------
# Import FastAPI's router, exception handling, request body parsing, and request object
from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import JSONResponse

# Import Python's built-in logging module for error/info logs
# Import traceback to capture detailed error stack traces
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Service responsible for validating and rotating refresh tokens
from ...auth.token_logic.refresh_token_service import refresh_token_service

# Service to enforce rate limiting and prevent abuse of endpoints
from ...auth.security.rate_limiter_service import rate_limiter_service

# Service that provides brute-force protection and login attempt tracking
from ...auth.security.login_protection_service import login_protection_service

# Schemas for validating refresh token requests and shaping token pair responses
from ...auth.token_logic.refresh_token_schema import (
    RefreshTokenSchema,        # Schema for incoming refresh token request
    TokenPairResponseSchema,   # Schema for returning both access + refresh tokens
)

# ---------------------------- Logger Setup ----------------------------
# Initialize logger for this module
logger = logging.getLogger(__name__)

# ---------------------------- Router ----------------------------
# Define FastAPI router for refresh token endpoints
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
    - Return both access + refresh tokens in HTTP-only cookies if valid
    - Raise 401 if refresh token is invalid or revoked
    - Raise 429 if too many attempts
    """
    try:
        # Extract client IP from request
        client_ip = request.client.host

        # Create Redis keys for rate limiting and login protection
        rate_key = f"refresh:ip:{client_ip}"
        lock_key = f"refresh:ip:{client_ip}"

        # ---------------------------- Rate Limiting ----------------------------
        # Ensure client is not exceeding refresh requests
        if not await rate_limiter_service.record_request(rate_key):
            raise HTTPException(
                status_code=429,
                detail="Too many refresh attempts. Try again later."
            )

        # ---------------------------- Login Protection Check ----------------------------
        # Block request if IP is locked due to too many failed attempts
        if await login_protection_service.is_locked(lock_key):
            raise HTTPException(
                status_code=429,
                detail="Too many failed refresh attempts. Try later."
            )

        # ---------------------------- Call Refresh Token Service ----------------------------
        # Attempt to refresh tokens using provided refresh token
        tokens = await refresh_token_service.refresh_tokens(payload.refresh_token)

        # ---------------------------- Handle Invalid Token ----------------------------
        # If service returns None, treat as invalid or revoked refresh token
        if not tokens:
            # Record failed attempt for this IP
            await login_protection_service.record_failed_attempt(lock_key)
            raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

        # ---------------------------- Successful Refresh ----------------------------
        # Reset failed attempts since refresh succeeded
        await login_protection_service.reset_failed_attempts(lock_key)

        # ---------------------------- Set Tokens in HTTP-only Cookies ----------------------------
        response = JSONResponse(content={"message": "Tokens refreshed successfully"})

        # Access token (1 hour expiry)
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=3600
        )

        # Refresh token (30 days expiry)
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=2592000
        )

        return response

    except Exception:
        # ---------------------------- Error Logging ----------------------------
        # Log full stack trace in case of unexpected error
        logger.error("Error in refresh tokens endpoint:\n%s", traceback.format_exc())
        # Raise generic 500 error for client
        raise HTTPException(status_code=500, detail="Internal Server Error")
