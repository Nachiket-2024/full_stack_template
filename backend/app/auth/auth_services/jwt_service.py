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
    """

    # ---------------------------- Create Access Token ----------------------------
    # Input: user identifier (email), table name
    # Output: JWT access token string
    @staticmethod
    async def create_access_token(email: str, table_name: str) -> str:
        """
        Generate a short-lived access token.
        """
        # Create a timezone-aware UTC expiration datetime
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        # Payload includes subject, table, and expiration timestamp
        payload: dict[str, str | float] = {
            "sub": email,          # Subject: user's email
            "table": table_name,   # Table name for role-specific user
            "exp": expire.timestamp()  # Expiration timestamp
        }
        # Encode the JWT with the secret key and algorithm
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token

    # ---------------------------- Create Refresh Token ----------------------------
    # Input: user identifier (email), table name
    # Output: JWT refresh token string
    @staticmethod
    async def create_refresh_token(email: str, table_name: str) -> str:
        """
        Generate a long-lived refresh token.
        """
        # Create a timezone-aware UTC expiration datetime
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        # Payload includes subject, table, and expiration timestamp
        payload: dict[str, str | float] = {
            "sub": email,
            "table": table_name,
            "exp": expire.timestamp()
        }
        # Encode the JWT using algorithm
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token

    # ---------------------------- Verify Token ----------------------------
    # Input: JWT token string
    # Output: payload dict if valid, None if invalid/expired
    @staticmethod
    async def verify_token(token: str) -> dict | None:
        """
        Verify access or refresh token.
        """
        try:
            # Decode the JWT with the secret key and allowed algorithms
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    # Input: JWT token string
    # Output: True if revoked successfully
    @staticmethod
    async def revoke_refresh_token(token: str) -> bool:
        """
        Revoke a refresh token by storing it in Redis blacklist.
        """
        try:
            # Decode the JWT to get expiration
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            exp_timestamp = payload.get("exp")
            # Compute TTL in seconds until token expiration
            ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp())
            # Only store in Redis if token is not expired
            if ttl > 0:
                await redis_client.set(f"revoked:{token}", "true", ex=ttl)
            return True
        except Exception:
            # On any error, revocation fails
            return False

    # ---------------------------- Check Token Revocation ----------------------------
    # Input: JWT token string
    # Output: True if revoked, False otherwise
    @staticmethod
    async def is_token_revoked(token: str) -> bool:
        """
        Check if a refresh token is revoked in Redis.
        """
        revoked = await redis_client.get(f"revoked:{token}")
        return revoked is not None

# ---------------------------- Service Instance ----------------------------
# Single instance for global use
jwt_service = JWTService()
