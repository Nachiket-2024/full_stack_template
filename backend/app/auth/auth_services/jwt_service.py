# ---------------------------- External Imports ----------------------------
# For datetime calculations with timezone awareness
from datetime import datetime, timedelta, timezone

# JWT encoding/decoding
import jwt

# ---------------------------- Internal Imports ----------------------------
# Load settings like SECRET_KEY, token expiration times
from ...core.settings import settings

# Async Redis client for token revocation
from ...redis.client import redis_client

# ---------------------------- JWT Service ----------------------------
class JWTService:
    """
    Service to handle JWT access and refresh tokens, including revocation via Redis.
    Tokens now include the user's role instead of table_name.
    With DB enforcing only one valid access+refresh per user, 
    Redis revocation acts as a "kill switch" for forced logout / stolen token invalidation.
    """

    # ---------------------------- Create Access Token ----------------------------
    @staticmethod
    async def create_access_token(email: str, role: str) -> str:
        """
        Generate a short-lived access token including user role.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload: dict[str, str | float] = {
            "sub": email,         # User email
            "role": role,         # User role
            "exp": expire.timestamp(),  # Expiration timestamp
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # ---------------------------- Create Refresh Token ----------------------------
    @staticmethod
    async def create_refresh_token(email: str, role: str) -> str:
        """
        Generate a long-lived refresh token including user role.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        payload: dict[str, str | float] = {
            "sub": email,
            "role": role,
            "exp": expire.timestamp(),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # ---------------------------- Verify Token ----------------------------
    @staticmethod
    async def verify_token(token: str) -> dict | None:
        """
        Verify access or refresh token and return payload if valid.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    @staticmethod
    async def revoke_refresh_token(token: str) -> bool:
        """
        Revoke a refresh token by storing it in Redis blacklist.
        Redis entry expires when the token itself expires.
        """
        try:
            # Decode without enforcing expiration check
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": False},
            )
            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                return False

            ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp())
            if ttl <= 0:
                return False

            await redis_client.set(f"revoked:{token}", "1", ex=ttl)
            return True
        except jwt.InvalidTokenError:
            return False
        except Exception:
            return False

    # ---------------------------- Check Token Revocation ----------------------------
    @staticmethod
    async def is_token_revoked(token: str) -> bool:
        """
        Check if a refresh token is revoked in Redis.
        """
        return await redis_client.get(f"revoked:{token}") is not None


# ---------------------------- Service Instance ----------------------------
jwt_service = JWTService()
