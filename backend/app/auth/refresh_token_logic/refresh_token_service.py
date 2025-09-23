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
        try:
            # Step 1: Check if refresh token is revoked
            if await jwt_service.is_token_revoked(refresh_token):
                logger.warning("Attempt to use revoked refresh token")
                return None

            # Step 2: Verify token payload and extract email
            payload = await jwt_service.verify_token(refresh_token)
            if not payload:
                return None
            
            email = payload.get("email")
            role = payload.get("role")
            
            if not email or not role:
                return None

            # Step 3: Revoke old refresh token in Redis
            await jwt_service.revoke_token(refresh_token, email)

            # Step 4: Generate new access token
            new_access_token = await jwt_service.create_access_token(email, role)

            # Step 5: Generate new refresh token
            new_refresh_token = await jwt_service.create_refresh_token(email, role)

            # Step 6: Return dictionary containing new tokens
            return {"access_token": new_access_token, "refresh_token": new_refresh_token}

        except Exception:
            logger.error("Error refreshing token:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    @staticmethod
    async def revoke_refresh_token(refresh_token: str) -> bool:
        try:
            # Step 1: Verify token payload
            payload = await jwt_service.verify_token(refresh_token)
            if not payload:
                return False

            # Step 2: Extract email from payload
            email = payload.get("email")
            if not email:
                return False

            # Step 3: Revoke refresh token in Redis
            await jwt_service.revoke_token(refresh_token, email)
            return True

        except Exception:
            logger.error("Error revoking refresh token:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Revoke All Tokens for User ----------------------------
    @staticmethod
    async def revoke_all_tokens_for_user(email: str) -> int:
        try:
            # Step 1: Fetch all refresh tokens for the user
            tokens = await jwt_service.get_all_refresh_tokens_for_user(email)
            if not tokens:
                return 0

            revoked_count = 0

            # Step 2: Revoke each token in Redis
            for token in tokens:
                if await jwt_service.revoke_token(token, email):
                    revoked_count += 1

            # Step 3: Return count of revoked tokens
            return revoked_count

        except Exception:
            logger.error("Error revoking all tokens for user %s:\n%s", email, traceback.format_exc())
            return 0


# ---------------------------- Singleton Instance ----------------------------
# Create single global instance of RefreshTokenService for application usage
refresh_token_service = RefreshTokenService()
