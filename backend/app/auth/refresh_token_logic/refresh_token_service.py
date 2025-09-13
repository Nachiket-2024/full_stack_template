# ---------------------------- External Imports ----------------------------
# Import logging module for async logging and tracing
import logging

# Import traceback module to capture full stack traces
import traceback

# ---------------------------- Internal Imports ----------------------------
# Import JWT service for token creation, verification, and revocation
from ..token_logic.jwt_service import jwt_service

# Import role → token table mapping for refresh tokens
from ...access_control.role_tables import TOKEN_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create logger instance specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Refresh Token Service Class ----------------------------
# Service class responsible for refresh token operations
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
            # Check if token is already revoked in Redis
            if await jwt_service.is_token_revoked(refresh_token):
                # Log warning about revoked token usage
                logger.warning("Attempt to use revoked refresh token")

                # Return None since token cannot be used
                return None

            # Verify refresh token and get payload
            payload = await jwt_service.verify_token(refresh_token)

            # If payload is invalid, log warning and return None
            if not payload:
                logger.warning("Invalid or expired refresh token")
                return None

            # Extract email and table from payload
            email = payload.get("email")
            table = payload.get("table")

            # Validate that email and table exist
            if not email or not table:
                logger.warning("Malformed refresh token payload")
                return None

            # Revoke the old refresh token in Redis
            await jwt_service.revoke_refresh_token(refresh_token)

            # Create new access token for the user
            new_access_token = await jwt_service.create_access_token(email, table)

            # Create new refresh token for the user
            new_refresh_token = await jwt_service.create_refresh_token(email, table)

            # Get the token table corresponding to the user's role
            token_table = TOKEN_TABLES.get(table)

            # Log error if no token table mapping exists
            if not token_table:
                logger.error(f"No token table mapping found for role: {table}")
                return None

            # Update refresh token in the database
            await token_table.update_refresh_token_by_access_token(db, refresh_token, new_refresh_token)

            # Return dictionary containing new tokens
            return {"access_token": new_access_token, "refresh_token": new_refresh_token}

        # Catch unexpected exceptions
        except Exception:
            # Log the full traceback for debugging
            logger.error("Unexpected error in refreshing tokens:\n%s", traceback.format_exc())

            # Return None on error
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
            # Verify token and get payload
            payload = await jwt_service.verify_token(refresh_token)

            # Return False if payload is invalid
            if not payload:
                return False

            # Extract email and table from payload
            email = payload.get("email")
            table = payload.get("table")

            # Return False if email or table missing
            if not email or not table:
                return False

            # Revoke token in Redis
            revoked = await jwt_service.revoke_refresh_token(refresh_token)

            # Get token table corresponding to role
            token_table = TOKEN_TABLES.get(table)

            # Update token table in DB to mark token as inactive
            if token_table:
                await token_table.update_refresh_token_by_access_token(db, refresh_token, new_refresh_token=None)

            # Return whether revocation in Redis succeeded
            return revoked

        except Exception:
            # Log unexpected errors with traceback
            logger.error("Unexpected error in revoking refresh token:\n%s", traceback.format_exc())

            # Return False on exception
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
            # Verify token and extract payload
            payload = await jwt_service.verify_token(refresh_token)

            # Return 0 if payload invalid
            if not payload:
                return 0

            # Extract email and table
            email = payload.get("email")
            table = payload.get("table")

            # Return 0 if email or table missing
            if not email or not table:
                return 0

            # Get token table for role
            token_table = TOKEN_TABLES.get(table)

            # Return 0 if no mapping exists
            if not token_table:
                logger.error(f"No token table mapping found for role: {table}")
                return 0

            # Fetch all refresh tokens for the user
            all_tokens = await token_table.get_all_refresh_tokens(email=email, db=db)
            
            # Return 0 if no tokens found
            if not all_tokens:
                return 0

            # Revoke all tokens in Redis
            revoked_count = await jwt_service.revoke_all_refresh_tokens_for_user(
                email=email, table=table, all_tokens=all_tokens
            )

            # Mark all tokens inactive in DB
            for token in all_tokens:
                await token_table.update_refresh_token_by_access_token(db, token, new_refresh_token=None)

            # Return total number of revoked tokens
            return revoked_count

        except Exception:
            # Log errors during mass revocation with traceback
            logger.error(
                "Error revoking all tokens for email from token %s:\n%s",
                refresh_token,
                traceback.format_exc(),
            )
            # Return 0 on exception
            return 0


# ---------------------------- Service Instance ----------------------------
# Singleton instance of RefreshTokenService for importing elsewhere
refresh_token_service = RefreshTokenService()
