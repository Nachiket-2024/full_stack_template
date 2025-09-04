# ---------------------------- External Imports ----------------------------
# Import FastAPI's router, request body parsing, and request object
from fastapi import APIRouter, Body, Request

# Import Python's built-in logging module for error/info logs
import logging

# ---------------------------- Internal Imports ----------------------------
# Schemas for validating refresh token requests and shaping token pair responses
from ...auth.refresh_token_logic.refresh_token_schema import (
    RefreshTokenSchema,        # Schema for incoming refresh token request
    TokenPairResponseSchema,   # Schema for returning both access + refresh tokens
)

# Import refresh token handler for processing logic
from ...auth.refresh_token_logic.refresh_token_handler import refresh_token_handler

# ---------------------------- Logger Setup ----------------------------
# Initialize logger for this module
logger = logging.getLogger(__name__)

# ---------------------------- Router ----------------------------
# Define FastAPI router for refresh token endpoints
router = APIRouter(prefix="/auth/refresh", tags=["Refresh Token"])

# ---------------------------- Refresh Tokens Endpoint ----------------------------
@router.post("/", response_model=TokenPairResponseSchema)
async def refresh_tokens(request: Request, payload: RefreshTokenSchema = Body(...)):
    # Delegate handling of refresh token logic to handler
    return await refresh_token_handler.handle_refresh_tokens(request, payload)
