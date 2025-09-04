# ---------------------------- External Imports ----------------------------
# For async logging and traceback
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Reuse JWT creation, verification, and revocation
from ..token_logic.jwt_service import jwt_service

# Role → DB table mapping for users
from ...access_control.role_tables import ROLE_TABLES

# Role → Token table mapping for refresh tokens
from ...access_control.role_tables import TOKEN_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create logger for this module
logger = logging.getLogger(__name__)

# ---------------------------- Refresh Token Service ----------------------------
class RefreshTokenService:

    # ---------------------------- Refresh Tokens ----------------------------
    @staticmethod
    async def refresh_tokens(refresh_token: str) -> dict[str, str] | None:

        try:
            # Step 1: Check if token already revoked in Redis
            if await jwt_service.is_token_revoked(refresh_token):
                logger.warning("Attempt to use revoked refresh token")
                return None

            # Step 2: Verify the refresh token payload
            payload = await jwt_service.verify_token(refresh_token)
            if not payload:
                logger.warning("Invalid or expired refresh token")
                return None

            # Extract email and table
            email, table = payload.get("email"), payload.get("table")
            if not email or not table:
                logger.warning("Malformed refresh token payload")
                return None

            # Step 3: Revoke the old refresh token
            await jwt_service.revoke_refresh_token(refresh_token)

            # Step 4: Issue new tokens
            new_access_token = await jwt_service.create_access_token(email, table)
            new_refresh_token = await jwt_service.create_refresh_token(email, table)

            # Step 5: Persist the new refresh token in DB (user table, not token table)
            user_table = ROLE_TABLES.get(table)
            if not user_table:
                logger.error(f"No user table mapping found for role: {table}")
                return None
            await user_table.update_refresh_token(email=email, refresh_token=new_refresh_token)

            # Return both new tokens
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            }

        # Handle unexpected errors gracefully
        except Exception:
            logger.error(
                "Unexpected error in refreshing tokens:\n%s",
                traceback.format_exc(),
            )
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    @staticmethod
    async def revoke_refresh_token(refresh_token: str) -> bool:

        try:
            # Use JWTService revoke method directly
            return await jwt_service.revoke_refresh_token(refresh_token)

        except Exception:
            logger.error(
                "Unexpected error in revoking refresh token:\n%s",
                traceback.format_exc(),
            )
            return False

    # ---------------------------- Revoke All Tokens for Email ----------------------------
    @staticmethod
    async def revoke_all_tokens_for_email(refresh_token: str, db) -> int:

        try:
            # Verify the refresh token payload
            payload = await jwt_service.verify_token(refresh_token)
            if not payload:
                return 0

            # Extract email and table from payload
            email, table = payload.get("email"), payload.get("table")
            if not email or not table:
                return 0

            # Get the correct token table object
            token_table_obj = TOKEN_TABLES.get(table)
            if not token_table_obj:
                logger.error(f"No token table mapping found for role: {table}")
                return 0

            # Fetch all refresh tokens for this user from the token table
            all_tokens = await token_table_obj.get_all_refresh_tokens(email=email, db=db)
            if not all_tokens:
                return 0

            # Delegate Redis revocation to JWTService
            revoked_count = await jwt_service.revoke_all_refresh_tokens_for_user(
                email=email,
                table=table,
                all_tokens=all_tokens,
            )
            return revoked_count

        except Exception:
            logger.error(
                "Error revoking all tokens for email from token %s:\n%s",
                refresh_token,
                traceback.format_exc(),
            )
            return 0


# ---------------------------- Service Instance ----------------------------
# Singleton instance to be imported in other modules
refresh_token_service = RefreshTokenService()
