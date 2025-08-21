# ---------------------------- External Imports ----------------------------
# Datetime utilities with timezone awareness
from datetime import datetime, timedelta, timezone

# JWT encoding and decoding library
import jwt

# ---------------------------- Internal Imports ----------------------------
# Application settings including SECRET_KEY and token expiration times
from ...core.settings import settings

# Async Redis client used for token revocation / blacklisting
from ...redis.client import redis_client

# ---------------------------- JWT Service ----------------------------
# Service to handle JWT access and refresh tokens, including revocation
class JWTService:
    """
    Handles JWT access and refresh tokens, including Redis-based revocation.
    Tokens include the user's table_name (role).
    Redis revocation acts as a "kill switch" for forced logout / stolen token invalidation.
    """

    # ---------------------------- Create Access Token ----------------------------
    # Generate a short-lived access token
    @staticmethod
    async def create_access_token(email: str, table: str) -> str:
        # Compute expiration timestamp
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        # JWT payload includes email, table, and expiration
        payload: dict[str, str | float] = {
            "email": email,
            "table": table,
            "exp": expire.timestamp(),
        }
        # Encode and return JWT
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # ---------------------------- Create Refresh Token ----------------------------
    # Generate a long-lived refresh token
    @staticmethod
    async def create_refresh_token(email: str, table: str) -> str:
        # Compute expiration timestamp
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        # JWT payload includes email, table, and expiration
        payload: dict[str, str | float] = {
            "email": email,
            "table": table,
            "exp": expire.timestamp(),
        }
        # Encode and return JWT
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # ---------------------------- Verify Token ----------------------------
    # Verify an access or refresh token and return its payload
    @staticmethod
    async def verify_token(token: str) -> dict | None:
        try:
            # Decode token using secret key and algorithm
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            # Token expired
            return None
        except jwt.InvalidTokenError:
            # Token invalid
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    # Revoke a refresh token by storing it in Redis with TTL
    @staticmethod
    async def revoke_refresh_token(token: str) -> bool:
        try:
            # Decode token without verifying expiration
            payload = jwt.decode(token, 
                                 settings.SECRET_KEY, 
                                 algorithms=[settings.JWT_ALGORITHM], 
                                 options={"verify_exp": False}
                                 )
            
            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                return False
            # Compute TTL for Redis key
            ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp())
            if ttl <= 0:
                return False
            # Store token in Redis blacklist
            await redis_client.set(f"revoked:{token}", "1", ex=ttl)
            return True
        except jwt.InvalidTokenError:
            return False
        except Exception:
            return False
        
    # ---------------------------- Revoke All Refresh Tokens for User ----------------------------
    # Revoke all refresh tokens for a specific email in a given table
    @staticmethod
    async def revoke_all_refresh_tokens_for_user(email: str, table: str, all_tokens: list[str]) -> int:
        """
        Revoke all provided refresh tokens for a user by storing each in Redis.

        Parameters:
        - email: user's email
        - table: user's role/table
        - all_tokens: list of refresh tokens to revoke

        Returns:
        - Number of tokens successfully revoked
        """
        revoked_count = 0

        for token in all_tokens:
            try:
                # Decode token without verifying expiration
                payload = jwt.decode(token, 
                                     settings.SECRET_KEY, 
                                     algorithms=[settings.JWT_ALGORITHM], 
                                     options={"verify_exp": False}
                                     )
                
                # Only revoke if token belongs to the same email & table
                if payload.get("email") == email and payload.get("table") == table:
                    exp_timestamp = payload.get("exp")
                    if exp_timestamp:
                        ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp())
                        if ttl > 0:
                            await redis_client.set(f"revoked:{token}", "1", ex=ttl)
                            revoked_count += 1
            except Exception:
                # Skip invalid tokens silently
                continue

        return revoked_count

    # ---------------------------- Check Token Revocation ----------------------------
    # Check if a refresh token is revoked in Redis
    @staticmethod
    async def is_token_revoked(token: str) -> bool:
        return await redis_client.get(f"revoked:{token}") is not None


# ---------------------------- Service Instance ----------------------------
# Singleton instance for JWT operations
jwt_service = JWTService()
