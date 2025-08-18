# ---------------------------- External Imports ----------------------------
# Pydantic BaseModel for request validation
from pydantic import BaseModel, Field

# ---------------------------- Refresh Token Schema ----------------------------
class RefreshTokenSchema(BaseModel):
    """
    Schema for refreshing access token using a refresh token.
    """
    refresh_token: str = Field(..., description="Valid refresh token issued previously")
