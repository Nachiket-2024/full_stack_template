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
# Service to handle JWT access and refresh tokens, including revocation
class JWTService:
    """
    1. create_access_token - Generate a short-lived JWT access token.
    2. create_refresh_token - Generate a long-lived JWT refresh token.
    3. verify_token - Verify a token and return its payload.
    4. revoke_refresh_token - Revoke a refresh token in Redis with TTL.
    5. revoke_all_refresh_tokens_for_user - Revoke all tokens for a given email.
    6. is_token_revoked - Check if a token is revoked in Redis.
    """

    # ---------------------------- Create Access Token ----------------------------
    @staticmethod
    async def create_access_token(email: str, table: str) -> str:
        """
        Input:
            1. email (str): User's email to encode in token.
            2. table (str): Role table name for token context.
        
        Process:
            1. Compute expiration timestamp based on settings.
            2. Prepare JWT payload with email, table, and exp.
            3. Encode payload with secret key and algorithm.

        Output:
            1. str: Encoded JWT access token.
        """
        # compute expiration timestamp for access token
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # prepare payload with email, table, and expiration
        payload: dict[str, str | float] = {"email": email, "table": table, "exp": expire.timestamp()}

        # encode payload into JWT token string
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # ---------------------------- Create Refresh Token ----------------------------
    @staticmethod
    async def create_refresh_token(email: str, table: str) -> str:
        """
        Input:
            1. email (str): User's email for token payload.
            2. table (str): Role table name for token payload.

        Process:
            1. Compute expiration timestamp for refresh token.
            2. Construct JWT payload with email, table, and exp.
            3. Encode payload with secret key and algorithm.

        Output:
            1. str: Encoded JWT refresh token.
        """
        # compute expiration timestamp for refresh token
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        # prepare payload with email, table, and expiration
        payload: dict[str, str | float] = {"email": email, "table": table, "exp": expire.timestamp()}

        # encode payload into JWT token string
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # ---------------------------- Verify Token ----------------------------
    @staticmethod
    async def verify_token(token: str) -> dict | None:
        """
        Input:
            1. token (str): JWT token to verify.

        Process:
            1. Decode token using secret key and algorithm.
            2. Catch ExpiredSignatureError and InvalidTokenError.

        Output:
            1. dict | None: Decoded payload or None if invalid/expired.
        """
        try:
            # decode JWT token with secret and algorithm
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

            # return decoded payload dictionary
            return payload

        # token expired case
        except jwt.ExpiredSignatureError:
            return None

        # invalid token case
        except jwt.InvalidTokenError:
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
            # decode token ignoring expiration validation
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})

            # get expiration timestamp from payload
            exp_timestamp = payload.get("exp")

            # if no expiration present then revoke fails
            if not exp_timestamp:
                return False

            # compute ttl in seconds from expiration - current time
            ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp())

            # if ttl is already expired then revoke fails
            if ttl <= 0:
                return False

            # store revoked token in redis with ttl
            await redis_client.set(f"revoked:{token}", "1", ex=ttl)

            # return success
            return True

        # invalid token error
        except jwt.InvalidTokenError:
            return False

        # any other unexpected error
        except Exception:
            return False

    # ---------------------------- Revoke All Refresh Tokens for User ----------------------------
    @staticmethod
    async def revoke_all_refresh_tokens_for_user(email: str, table: str, all_tokens: list[str]) -> int:
        """
        Input:
            1. email (str): User email to revoke tokens for.
            2. table (str): Role table name for token scope.
            3. all_tokens (list[str]): List of user's refresh tokens.

        Process:
            1. Loop through all tokens and decode each without expiration check.
            2. Check if token belongs to given email and table.
            3. Compute TTL and store in Redis if valid.
            4. Count total revoked tokens.

        Output:
            1. int: Number of tokens successfully revoked.
        """
        # initialize revoked counter
        revoked_count = 0

        # iterate through all provided tokens
        for token in all_tokens:
            try:
                # decode token ignoring expiration
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})

                # check if token belongs to given email and table
                if payload.get("email") == email and payload.get("table") == table:
                    # extract expiration timestamp
                    exp_timestamp = payload.get("exp")

                    # if expiration exists
                    if exp_timestamp:
                        # compute ttl seconds
                        ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp())

                        # if ttl is valid positive
                        if ttl > 0:
                            # store revoked token in redis with ttl
                            await redis_client.set(f"revoked:{token}", "1", ex=ttl)

                            # increment revoked count
                            revoked_count += 1

            # skip invalid or broken tokens
            except Exception:
                continue

        # return total revoked tokens
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
        # check redis if token exists in revoked set
        return await redis_client.get(f"revoked:{token}") is not None


# ---------------------------- Service Instance ----------------------------
# Singleton instance for JWT operations
jwt_service = JWTService()
