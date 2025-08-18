# ---------------------------- External Imports ----------------------------
# FastAPI router and request handling
from fastapi import APIRouter, HTTPException, Body

# For async logging and traceback
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Refresh token service to issue new access tokens
from ..auth_services.refresh_token_service import refresh_token_service

# Schemas for request/response validation
from ..auth_schemas.refresh_token_schema import RefreshTokenSchema

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Router ----------------------------
router = APIRouter(prefix="/auth/refresh", tags=["Refresh Token"])

# ---------------------------- Refresh Access Token Endpoint ----------------------------
@router.post("/")
async def refresh_access_token(payload: RefreshTokenSchema = Body(...)):
    """
    Refresh access token using a valid refresh token.
    Returns a new access token if refresh token is valid and not revoked.
    """
    try:
        # Call refresh token service to get a new access token
        new_access_token = await refresh_token_service.refresh_access_token(payload.refresh_token)

        # If token is invalid or revoked, raise HTTP 401
        if not new_access_token:
            raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

        return {"access_token": new_access_token}

    except Exception:
        # Log full traceback for debugging
        logger.error("Error in refresh access token endpoint:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")
