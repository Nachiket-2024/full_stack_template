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

# ---------------------------- JWT Service Class ----------------------------
# Service to handle JWT access and refresh tokens using Redis only
class JWTService:
    """
    1. create_access_token - Generate a short-lived JWT access token.
    2. create_refresh_token - Generate a long-lived JWT refresh token.
    3. verify_token - Verify a token and return its payload.
    4. revoke_refresh_token - Revoke a refresh token in Redis.
    5. revoke_all_refresh_tokens_for_user - Revoke all tokens for a user in Redis.
    6. is_token_revoked - Check if a token is revoked in Redis.
    """

    # ---------------------------- Create Access Token ----------------------------
    @staticmethod
    async def create_access_token(user_id: str, device_id: str) -> str:
        """
        Input:
            1. user_id (str): User identifier.
            2. device_id (str): Device identifier for token context.

        Process:
            1. Compute expiration timestamp for access token.
            2. Prepare JWT payload with user_id, device_id, and exp.
            3. Encode payload with secret key and algorithm.

        Output:
            1. str: Encoded JWT access token.
        """
        # -------1. Compute expiration timestamp for access token-------
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # -------2. Prepare JWT payload with user_id, device_id, and exp-------
        payload: dict[str, str | float] = {"user_id": user_id, "device_id": device_id, "exp": expire.timestamp()}

        # -------3. Encode payload with secret key and algorithm-------
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # ---------------------------- Create Refresh Token ----------------------------
    @staticmethod
    async def create_refresh_token(user_id: str, device_id: str) -> str:
        """
        Input:
            1. user_id (str): User identifier.
            2. device_id (str): Device identifier for token context.

        Process:
            1. Compute expiration timestamp for refresh token.
            2. Construct JWT payload with user_id, device_id, and exp.
            3. Encode payload with secret key and algorithm.

        Output:
            1. str: Encoded JWT refresh token.
        """
        # -------1. Compute expiration timestamp for refresh token-------
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        # -------2. Construct JWT payload with user_id, device_id, and exp-------
        payload: dict[str, str | float] = {"user_id": user_id, "device_id": device_id, "exp": expire.timestamp()}

        # -------3. Encode payload with secret key and algorithm-------
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # ---------------------------- Verify Token ----------------------------
    @staticmethod
    async def verify_token(token: str) -> dict | None:
        """
        Input:
            1. token (str): JWT token to verify.

        Process:
            1. Decode token using secret key and algorithm.
            2. Catch expired or invalid token errors.

        Output:
            1. dict | None: Decoded payload or None if invalid/expired.
        """
        try:
            # -------1. Decode token using secret key and algorithm-------
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        except jwt.ExpiredSignatureError:
            # -------2. Catch expired token error-------
            return None
        
        except jwt.InvalidTokenError:
            # -------2. Catch invalid token error-------
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    @staticmethod
    async def revoke_refresh_token(token: str) -> bool:
        """
        Input:
            1. token (str): Refresh token to revoke.

        Process:
            1. Decode token without verifying expiration.
            2. Compute TTL for Redis key from exp.
            3. Store token in Redis with TTL.

        Output:
            1. bool: True if successfully revoked, False otherwise.
        """
        try:
            # -------1. Decode token without verifying expiration-------
            payload = jwt.decode(token, 
                                 settings.SECRET_KEY, 
                                 algorithms=[settings.JWT_ALGORITHM], 
                                 options={"verify_exp": False}
                                )
            
            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                return False

            # -------2. Compute TTL for Redis key from exp-------
            ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp())

            if ttl <= 0:
                return False

            # -------3. Store token in Redis with TTL-------
            await redis_client.set(f"revoked:{token}", "1", ex=ttl)
            return True
        
        except jwt.InvalidTokenError:
            return False
        
        except Exception:
            return False

    # ---------------------------- Revoke All Tokens for User ----------------------------
    @staticmethod
    async def revoke_all_refresh_tokens_for_user(all_tokens: list[str]) -> int:
        """
        Input:
            1. all_tokens (list[str]): List of refresh tokens for a user.

        Process:
            1. Loop through all tokens and decode each without expiration check.
            2. Compute TTL and store in Redis if valid.
            3. Count total revoked tokens.

        Output:
            1. int: Number of tokens successfully revoked.
        """
        revoked_count = 0

        for token in all_tokens:
            try:
                # -------1. Decode each token without expiration check-------
                payload = jwt.decode(token, 
                                     settings.SECRET_KEY, 
                                     algorithms=[settings.JWT_ALGORITHM], 
                                     options={"verify_exp": False}
                                    )
                exp_timestamp = payload.get("exp")

                if exp_timestamp:
                    # -------2. Compute TTL and store in Redis if valid-------
                    ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp())

                    if ttl > 0:
                        await redis_client.set(f"revoked:{token}", "1", ex=ttl)

                        # -------3. Count total revoked tokens-------
                        revoked_count += 1
            except Exception:
                continue
        return revoked_count

    # ---------------------------- Check Token Revocation ----------------------------
    @staticmethod
    async def is_token_revoked(token: str) -> bool:
        """
        Input:
            1. token (str): Refresh token to check revocation status.

        Process:
            1. Query Redis to see if token is blacklisted.

        Output:
            1. bool: True if token is revoked, False otherwise.
        """
        # -------1. Query Redis to see if token is blacklisted-------
        return await redis_client.get(f"revoked:{token}") is not None


# ---------------------------- Service Instance ----------------------------
# Singleton instance for JWT operations
jwt_service = JWTService()
