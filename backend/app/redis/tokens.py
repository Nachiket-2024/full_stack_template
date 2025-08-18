# ---------------------------- Internal Imports ----------------------------
# Async Redis client
from .client import redis_client

# ---------------------------- Token Revocation ----------------------------
class TokenService:
    """
    Service to handle refresh token revocation and status checks.
    """

    # ---------------------------- Revoke Token ----------------------------
    # Input: token string, expiration in seconds
    # Output: None
    @staticmethod
    async def revoke_token(token: str, expires_seconds: int) -> None:
        """
        Store a revoked token in Redis with TTL (time-to-live).
        """
        await redis_client.set(f"revoked:{token}", "true", ex=expires_seconds)

    # ---------------------------- Check Token Revocation ----------------------------
    # Input: token string
    # Output: True if revoked, False otherwise
    @staticmethod
    async def is_token_revoked(token: str) -> bool:
        """
        Check if a token exists in the revoked list.
        """
        revoked = await redis_client.get(f"revoked:{token}")
        return revoked is not None

# ---------------------------- Service Instance ----------------------------
# Single instance for global use
token_service = TokenService()
