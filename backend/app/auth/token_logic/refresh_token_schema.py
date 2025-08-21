# ---------------------------- External Imports ----------------------------
# Pydantic BaseModel for request/response validation
from pydantic import BaseModel, Field

# ---------------------------- Refresh Token Request Schema ----------------------------
class RefreshTokenSchema(BaseModel):
    """
    Request schema for refreshing access token using a refresh token.
    """
    refresh_token: str = Field(..., description="Valid refresh token issued previously")

# ---------------------------- Token Pair Response Schema ----------------------------
class TokenPairResponseSchema(BaseModel):
    """
    Response schema for returning a new pair of tokens (access + refresh).
    Used in signup, login, and refresh flows.
    """
    access_token: str = Field(..., description="Newly issued access token")
    refresh_token: str = Field(..., description="Newly issued refresh token")
