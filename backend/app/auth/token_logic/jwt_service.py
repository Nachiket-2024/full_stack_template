# ---------------------------- External Imports ----------------------------
# Import datetime utilities with timezone awareness
from datetime import datetime, timedelta, timezone

# Import asyncio for running blocking operations in a thread pool
import asyncio

# Import JWT encoding and decoding library
import jwt

# Logging for structured event and error logging
import logging

# Capture full stack traces in case of exceptions
import traceback

# ---------------------------- Internal Imports ----------------------------
# Import application settings including SECRET_KEY and token expiration times
from ...core.settings import settings

# Import async Redis client used for token revocation / blacklisting
from ...redis.client import redis_client

# ---------------------------- Logger Setup ----------------------------
# Create logger instance specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- JWT Service Class ----------------------------
# Define service class for creating, verifying, revoking, and managing JWT tokens
class JWTService:
    """
    1. create_access_token - Generate short-lived access token with email and role.
    2. create_refresh_token - Generate refresh token with email and role, store in Redis.
    3. verify_token - Decode and validate token, check revocation.
    4. revoke_token - Revoke token and optionally remove from user set.
    5. is_token_revoked - Check if token is revoked in Redis.
    6. get_all_refresh_tokens_for_user - Fetch all refresh tokens of a user.
    """

    # ---------------------------- Create Access Token ----------------------------
    async def create_access_token(self, email: str, role: str) -> str:
        """
        Input:
            1. email (str): Email address of the user.
            2. role (str): Role assigned to the user.

        Process:
            1. Compute expiry timestamp for access token.
            2. Create token payload with email, role, and expiration.
            3. Encode payload asynchronously using secret key.

        Output:
            1. str: Encoded JWT access token.
        """
        # Step 1: Compute expiry timestamp for access token
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Step 2: Create token payload with email, role, and expiration
        payload = {"email": email, "role": role, "exp": expire}

        # Step 3: Encode payload asynchronously using secret key
        return await asyncio.to_thread(jwt.encode, payload, settings.SECRET_KEY, settings.JWT_ALGORITHM)

    # ---------------------------- Create Refresh Token ----------------------------
    async def create_refresh_token(self, email: str, role: str) -> str:
        """
        Input:
            1. email (str): Email address of the user.
            2. role (str): Role assigned to the user.

        Process:
            1. Compute expiry timestamp for refresh token.
            2. Create token payload with email, role, and expiration.
            3. Encode payload asynchronously into JWT token.
            4. Store refresh token in Redis set for user.
            5. Return refresh token.

        Output:
            1. str: Encoded JWT refresh token.
        """
        # Step 1: Compute expiry timestamp for refresh token
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        # Step 2: Create token payload with email, role, and expiration
        payload = {"email": email, "role": role, "exp": expire}

        # Step 3: Encode payload asynchronously into JWT token
        token = await asyncio.to_thread(jwt.encode, payload, settings.SECRET_KEY, settings.JWT_ALGORITHM)

        # Step 4: Store refresh token in Redis set for user
        await redis_client.sadd(f"user:{email}:refresh_tokens", token)

        # Step 5: Return refresh token
        return token

    # ---------------------------- Verify Token ----------------------------
    async def verify_token(self, token: str) -> dict | None:
        """
        Input:
            1. token (str): Encoded JWT token.

        Process:
            1. Decode token asynchronously using secret key.
            2. Check if token is revoked in Redis.
            3. Return payload if valid.

        Output:
            1. dict | None: Decoded payload or None if invalid/revoked.
        """
        try:
            # Step 1: Decode token asynchronously using secret key
            payload = await asyncio.to_thread(jwt.decode, token, settings.SECRET_KEY, settings.JWT_ALGORITHM)

            # Step 2: Check if token is revoked in Redis
            if await self.is_token_revoked(token):
                return None

            # Step 3: Return payload if valid
            return payload

        except jwt.ExpiredSignatureError:
            # Token expired
            return None

        except jwt.InvalidTokenError:
            # Token invalid
            return None

        except Exception:
            # Handle unexpected exceptions and log errors
            logger.error("JWT verification error:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Revoke Token ----------------------------
    async def revoke_token(self, token: str, email: str | None = None) -> bool:
        """
        Input:
            1. token (str): Encoded JWT token.
            2. email (str | None): Email identifier (optional).

        Process:
            1. Decode token asynchronously to get expiry timestamp.
            2. Calculate TTL until token expiry.
            3. Store revoked token in Redis with TTL.
            4. Remove from user refresh token set if email provided.
            5. Return True on success, False on failure.

        Output:
            1. bool: True if revoked, False otherwise.
        """
        try:
            # Step 1: Decode token asynchronously to get expiry timestamp
            payload = await asyncio.to_thread(jwt.decode, token, settings.SECRET_KEY, settings.JWT_ALGORITHM)
            exp = payload.get("exp")

            # Step 2: Calculate TTL until token expiry
            ttl = max(0, int(exp - datetime.now(timezone.utc).timestamp()))

            # Step 3: Store revoked token in Redis with TTL
            await redis_client.setex(f"revoked:{token}", ttl, "true")

            # Step 4: Remove from user refresh token set if email provided
            if email:
                await redis_client.srem(f"user:{email}:refresh_tokens", token)

            return True  # Step 5: Return True on success

        except Exception:
            # Fail silently but log warning
            logger.warning("Failed to revoke token: %s\n%s", token, traceback.format_exc())
            return False

    # ---------------------------- Check Token Revocation ----------------------------
    async def is_token_revoked(self, token: str) -> bool:
        """
        Input:
            1. token (str): Encoded JWT token.

        Process:
            1. Query Redis for revoked token key.

        Output:
            1. bool: True if revoked, False otherwise.
        """
        # Step 1: Query Redis for revoked token key and return True if revoked key exists in Redis
        return await redis_client.exists(f"revoked:{token}") == 1

    # ---------------------------- Get All Refresh Tokens ----------------------------
    async def get_all_refresh_tokens_for_user(self, email: str) -> list[str]:
        """
        Input:
            1. email (str): Email address of the user.

        Process:
            1. Fetch refresh tokens from Redis set for user.
            2. Return tokens as a list (already strings).

        Output:
            1. list[str]: List of refresh tokens.
        """
        # Step 1: Fetch refresh tokens from Redis set for user
        tokens = await redis_client.smembers(f"user:{email}:refresh_tokens")

        # Step 2: Return tokens as a list (already strings)
        return list(tokens) if tokens else []


# ---------------------------- Singleton Instance ----------------------------
# Create single global instance of JWTService for application usage
jwt_service = JWTService()
