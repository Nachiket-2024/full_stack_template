# ---------------------------- External Imports ----------------------------
# Logging for structured event and error logging
import logging

# Capture full stack traces in case of exceptions
import traceback

# ---------------------------- Internal Imports ----------------------------
# Import JWT service for token creation, verification, and revocation
from ..token_logic.jwt_service import jwt_service

# ---------------------------- Logger Setup ----------------------------
# Create logger instance specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Refresh Token Service Class ----------------------------
# Service class responsible for refresh token operations using Redis only
class RefreshTokenService:
    """
    1. refresh_tokens - Rotate refresh token and generate new access token.
    2. revoke_refresh_token - Revoke a single refresh token in Redis.
    3. revoke_all_tokens_for_user - Revoke all refresh tokens for a user in Redis.
    """

    # ---------------------------- Refresh Tokens ----------------------------
    @staticmethod
    async def refresh_tokens(refresh_token: str) -> dict[str, str] | None:
        """
        Input:
            1. refresh_token (str): Existing refresh token to be rotated.

        Process:
            1. Check if refresh token is revoked.
            2. Verify token payload and extract user ID.
            3. Revoke old refresh token in Redis.
            4. Generate new access token.
            5. Generate new refresh token.
            6. Return dictionary containing new tokens.

        Output:
            1. dict | None: New tokens or None if failure.
        """
        try:
            # Step 1: Check if refresh token is revoked
            if await jwt_service.is_token_revoked(refresh_token):
                logger.warning("Attempt to use revoked refresh token")
                return None

            # Step 2: Verify token payload and extract user ID
            payload = await jwt_service.verify_token(refresh_token)
            if not payload:
                return None
            user_id = payload.get("sub")
            if not user_id:
                return None

            # Step 3: Revoke old refresh token in Redis
            await jwt_service.revoke_token(refresh_token, user_id)

            # Step 4: Generate new access token
            new_access_token = await jwt_service.create_access_token(user_id)

            # Step 5: Generate new refresh token
            new_refresh_token = await jwt_service.create_refresh_token(user_id)

            # Step 6: Return dictionary containing new tokens
            return {"access_token": new_access_token, "refresh_token": new_refresh_token}

        except Exception:
            # Log any unexpected exceptions with full stack trace
            logger.error("Error refreshing token:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    @staticmethod
    async def revoke_refresh_token(refresh_token: str) -> bool:
        """
        Input:
            1. refresh_token (str): Refresh token to revoke.

        Process:
            1. Verify token payload.
            2. Extract user ID from payload.
            3. Revoke refresh token in Redis.

        Output:
            1. bool: True if revoked, False otherwise.
        """
        try:
            # Step 1: Verify token payload
            payload = await jwt_service.verify_token(refresh_token)
            if not payload:
                return False

            # Step 2: Extract user ID from payload
            user_id = payload.get("sub")
            if not user_id:
                return False

            # Step 3: Revoke refresh token in Redis
            await jwt_service.revoke_token(refresh_token, user_id)
            return True

        except Exception:
            # Log any unexpected exceptions with full stack trace
            logger.error("Error revoking refresh token:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Revoke All Tokens for User ----------------------------
    @staticmethod
    async def revoke_all_tokens_for_user(user_id: str) -> int:
        """
        Input:
            1. user_id (str): User identifier.

        Process:
            1. Fetch all refresh tokens for the user.
            2. Revoke each token in Redis.
            3. Return count of revoked tokens.

        Output:
            1. int: Number of tokens revoked.
        """
        try:
            # Step 1: Fetch all refresh tokens for the user
            tokens = await jwt_service.get_all_refresh_tokens_for_user(user_id)
            if not tokens:
                return 0

            revoked_count = 0

            # Step 2: Revoke each token in Redis
            for token in tokens:
                if await jwt_service.revoke_token(token, user_id):
                    revoked_count += 1

            # Step 3: Return count of revoked tokens
            return revoked_count

        except Exception:
            # Log any unexpected exceptions with full stack trace
            logger.error("Error revoking all tokens for user %s:\n%s", user_id, traceback.format_exc())
            return 0


# ---------------------------- Singleton Instance ----------------------------
# Create single global instance of RefreshTokenService for application usage
refresh_token_service = RefreshTokenService()
