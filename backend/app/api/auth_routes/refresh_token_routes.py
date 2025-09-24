# ---------------------------- External Imports ----------------------------
# Import FastAPI's router, request body parsing, and request object
from fastapi import APIRouter, Body, Request

# ---------------------------- Internal Imports ----------------------------
# Schemas for validating refresh token requests and shaping token pair responses
from ...auth.refresh_token_logic.refresh_token_schema import (
    RefreshTokenSchema,        # Schema for incoming refresh token request
    TokenPairResponseSchema,   # Schema for returning both access + refresh tokens
)

# Import refresh token handler for processing logic
from ...auth.refresh_token_logic.refresh_token_handler import refresh_token_handler

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Router ----------------------------
# Define FastAPI router for refresh token endpoints
router = APIRouter(prefix="/auth/refresh", tags=["Refresh Token"])

# ---------------------------- Refresh Tokens Endpoint ----------------------------
@router.post("/", response_model=TokenPairResponseSchema)
async def refresh_tokens(request: Request, payload: RefreshTokenSchema = Body(...)):
    """
    Input:
        1. request (Request): FastAPI request object for accessing cookies/headers.
        2. payload (RefreshTokenSchema): Incoming refresh token from client request.

    Process:
        1. Delegate handling of refresh token validation and new token issuance to refresh_token_handler.

    Output:
        1. TokenPairResponseSchema: Response containing new access and refresh tokens or error.
    """
    # Delegate handling of refresh token logic to handler
    return await refresh_token_handler.handle_refresh_tokens(request, payload)
