# ---------------------------- External Imports ----------------------------
# For async logging and traceback
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# JWT creation, verification, and revocation service
from ..token_logic.jwt_service import jwt_service

# Role → Token table mapping for refresh tokens
from ...access_control.role_tables import TOKEN_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create module-specific logger
logger = logging.getLogger(__name__)

# ---------------------------- Refresh Token Service Class ----------------------------
# Service class responsible for handling refresh token operations
class RefreshTokenService:
    """
    1. refresh_tokens - Refresh access and refresh tokens for a user and update token table.
    2. revoke_refresh_token - Revoke a single refresh token.
    3. revoke_all_tokens_for_email - Revoke all refresh tokens for a given email.
    """

    # ---------------------------- Refresh Tokens ----------------------------
    @staticmethod
    async def refresh_tokens(refresh_token: str, db) -> dict[str, str] | None:
        """
        Input:
            1. refresh_token (str): Existing refresh token to be rotated.
            2. db: Database session for token table operations.

        Process:
            1. Check if refresh token is already revoked in Redis.
            2. Verify refresh token payload and extract email/table info.
            3. Revoke old refresh token in Redis.
            4. Generate new access and refresh tokens.
            5. Persist new refresh token in the corresponding token table.

        Output:
            1. dict: Contains new access_token and refresh_token or None on failure.
        """
        try:
            # ---------------------------- Check Revocation ----------------------------
            # Return None if token is already revoked
            if await jwt_service.is_token_revoked(refresh_token):
                logger.warning("Attempt to use revoked refresh token")
                return None

            # ---------------------------- Verify Token ----------------------------
            # Verify refresh token payload
            payload = await jwt_service.verify_token(refresh_token)
            # Return None if payload is invalid
            if not payload:
                logger.warning("Invalid or expired refresh token")
                return None

            # Extract email and role table from payload
            email, table = payload.get("email"), payload.get("table")
            # Return None if email or table missing
            if not email or not table:
                logger.warning("Malformed refresh token payload")
                return None

            # ---------------------------- Revoke Old Token ----------------------------
            # Revoke old refresh token in Redis
            await jwt_service.revoke_refresh_token(refresh_token)

            # ---------------------------- Generate New Tokens ----------------------------
            # Create new access token
            new_access_token = await jwt_service.create_access_token(email, table)
            # Create new refresh token
            new_refresh_token = await jwt_service.create_refresh_token(email, table)

            # ---------------------------- Persist New Token ----------------------------
            # Get token table corresponding to user's role
            token_table = TOKEN_TABLES.get(table)
            # Log and return None if table mapping not found
            if not token_table:
                logger.error(f"No token table mapping found for role: {table}")
                return None

            # Update refresh token in database
            await token_table.update_refresh_token_by_access_token(db, refresh_token, new_refresh_token)

            # ---------------------------- Return Tokens ----------------------------
            # Return dictionary containing new tokens
            return {"access_token": new_access_token, "refresh_token": new_refresh_token}

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log unexpected errors with traceback
            logger.error("Unexpected error in refreshing tokens:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    @staticmethod
    async def revoke_refresh_token(refresh_token: str, db) -> bool:
        """
        Input:
            1. refresh_token (str): Refresh token to revoke.
            2. db: Database session for token table update.

        Process:
            1. Verify token payload to extract email/table.
            2. Revoke token in Redis.
            3. Mark token inactive in corresponding token table.

        Output:
            1. bool: True if successfully revoked, False otherwise.
        """
        try:
            # ---------------------------- Verify Token ----------------------------
            payload = await jwt_service.verify_token(refresh_token)
            if not payload:
                return False

            # Extract email and role table
            email, table = payload.get("email"), payload.get("table")
            if not email or not table:
                return False

            # ---------------------------- Revoke in Redis ----------------------------
            revoked = await jwt_service.revoke_refresh_token(refresh_token)

            # ---------------------------- Update Token Table ----------------------------
            token_table = TOKEN_TABLES.get(table)
            if token_table:
                await token_table.update_refresh_token_by_access_token(db, refresh_token, new_refresh_token=None)

            # Return whether revocation succeeded in Redis
            return revoked

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log unexpected errors with traceback
            logger.error("Unexpected error in revoking refresh token:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Revoke All Tokens for Email ----------------------------
    @staticmethod
    async def revoke_all_tokens_for_email(refresh_token: str, db) -> int:
        """
        Input:
            1. refresh_token (str): Refresh token to extract email for revocation.
            2. db: Database session for token table updates.

        Process:
            1. Verify token payload and extract email/table info.
            2. Fetch all refresh tokens for the user from the token table.
            3. Revoke all tokens in Redis.
            4. Mark all tokens inactive in token table.

        Output:
            1. int: Number of tokens successfully revoked.
        """
        try:
            # ---------------------------- Verify Token ----------------------------
            payload = await jwt_service.verify_token(refresh_token)
            if not payload:
                return 0

            # Extract email and role table from payload
            email, table = payload.get("email"), payload.get("table")
            if not email or not table:
                return 0

            # ---------------------------- Fetch Token Table ----------------------------
            token_table = TOKEN_TABLES.get(table)
            if not token_table:
                logger.error(f"No token table mapping found for role: {table}")
                return 0

            # ---------------------------- Fetch All Tokens ----------------------------
            all_tokens = await token_table.get_all_refresh_tokens(email=email, db=db)
            if not all_tokens:
                return 0

            # ---------------------------- Revoke Tokens in Redis ----------------------------
            revoked_count = await jwt_service.revoke_all_refresh_tokens_for_user(
                email=email, table=table, all_tokens=all_tokens
            )

            # ---------------------------- Mark Tokens Inactive in DB ----------------------------
            for token in all_tokens:
                await token_table.update_refresh_token_by_access_token(db, token, new_refresh_token=None)

            # Return total revoked count
            return revoked_count

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log unexpected errors with traceback
            logger.error(
                "Error revoking all tokens for email from token %s:\n%s",
                refresh_token,
                traceback.format_exc(),
            )
            return 0


# ---------------------------- Service Instance ----------------------------
# Singleton instance to be imported in other modules
refresh_token_service = RefreshTokenService()
