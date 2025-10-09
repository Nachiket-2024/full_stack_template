# ---------------------------- External Imports ----------------------------
# Pydantic BaseModel for request/response validation
from pydantic import BaseModel, Field

# ---------------------------- Refresh Token Request Schema ----------------------------
class RefreshTokenSchema(BaseModel):

    refresh_token: str = Field(..., description="Valid refresh token issued previously")

# ---------------------------- Token Pair Response Schema ----------------------------
class TokenPairResponseSchema(BaseModel):

    access_token: str = Field(..., description="Newly issued access token")
    refresh_token: str = Field(..., description="Newly issued refresh token")
