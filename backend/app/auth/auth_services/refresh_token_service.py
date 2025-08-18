# ---------------------------- External Imports ----------------------------
# For datetime calculations
from datetime import datetime, timedelta

# For async logging and traceback
import logging
import traceback

# JWT encoding/decoding
import jwt

# ---------------------------- Internal Imports ----------------------------
# Load settings like SECRET_KEY and token expiration times
from ...core.settings import settings

# Async Redis client for token revocation
from ...redis.client import redis_client

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Refresh Token Service ----------------------------
class RefreshTokenService:
    """
    Service to handle issuing new access tokens using refresh tokens
    and checking revocation.
    """

    # ---------------------------- Refresh Access Token ----------------------------
    # Input: refresh token string
    # Output: new access token string or None if invalid/revoked
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> str | None:
        """
        Verify refresh token and issue new access token.
        """
        try:
            # Check if token is revoked
            revoked = await redis_client.get(f"revoked:{refresh_token}")
            if revoked:
                logger.warning("Attempt to use revoked refresh token")
                return None

            # Decode refresh token
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
            email = payload.get("sub")
            role = payload.get("table")

            # Issue new access token
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            new_payload: dict[str, str | float] = {
                "sub": email,
                "table": role,
                "exp": expire.timestamp()
            }
            access_token = jwt.encode(new_payload, settings.SECRET_KEY, algorithm="HS256")
            return access_token

        except jwt.ExpiredSignatureError:
            logger.warning("Expired refresh token used")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid refresh token used")
            return None
        except Exception:
            logger.error("Error in refreshing access token:\n%s", traceback.format_exc())
            return None
        
    # ---------------------------- Revoke Refresh Token ----------------------------
    @staticmethod
    async def revoke_refresh_token(refresh_token: str) -> bool:
        """
        Revoke a refresh token by adding it to Redis.
        Returns True if revoked successfully, False if invalid.
        """
        try:
            # Optionally decode to validate token before revoking
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
            # Store in Redis with expiration matching the token's expiry
            exp = payload.get("exp")
            ttl = int(exp - datetime.utcnow().timestamp())
            await redis_client.set(f"revoked:{refresh_token}", "1", ex=ttl)
            return True
        except jwt.InvalidTokenError:
            return False
        except Exception:
            logger.error("Error in revoking refresh token:\n%s", traceback.format_exc())
            return False


# ---------------------------- Service Instance ----------------------------
# Single instance for global use
refresh_token_service = RefreshTokenService()
