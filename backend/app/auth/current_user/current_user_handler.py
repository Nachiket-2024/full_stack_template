# ---------------------------- External Imports ----------------------------
# Logging module for tracking errors and events
import logging

# Module to capture full stack traces for debugging exceptions
import traceback

# SQLAlchemy exceptions for handling DB errors
from sqlalchemy.exc import SQLAlchemyError

# ---------------------------- Internal Imports ----------------------------
# JWT service to decode and verify access tokens
from ..token_logic.jwt_service import jwt_service

# Role tables for querying user based on role (we'll call it 'table' in JWT for consistency)
from ...access_control.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- Current User Handler Class ----------------------------
# Handler class to manage fetching the currently authenticated user
class CurrentUserHandler:
    """
    Handles retrieval of current authenticated user:
    - Verifies JWT access token
    - Extracts user email and table (same as role)
    - Fetches user from database
    """

    # ---------------------------- Get Current User ----------------------------
    # Main method to fetch user from access token
    async def get_current_user(self, access_token: str, db) -> dict | None:
        """
        Retrieves current user info using JWT access token.
        Params:
        - access_token: JWT access token from request cookie
        - db: Async database session
        Returns:
        - dict with user info (name, email, table/role) or error if invalid
        """
        try:
            if not access_token:
                return {"error": "No access token provided"}

            # Verify token using actual JWT service
            payload = await jwt_service.verify_token(access_token)
            if not payload:
                return {"error": "Invalid or expired token"}

            email = payload.get("email")
            table = payload.get("table")  # using 'table' for consistency with JWT; same as role

            if not email or not table:
                return {"error": "Invalid token payload"}

            # Get the correct CRUD table based on table (role)
            crud_instance = ROLE_TABLES.get(table)
            if not crud_instance:
                return {"error": "User table/role not found"}

            # Fetch user from database
            user = await crud_instance.get_by_email(db, email)
            if not user:
                return {"error": "User not found"}

            # Return basic user info
            return {
                "name": getattr(user, "name", "Unknown"),
                "email": getattr(user, "email", None),
                "table": table  # same as role
            }

        except SQLAlchemyError:
            # Log database errors
            logger.error("Database error fetching current user:\n%s", traceback.format_exc())
            return {"error": "Database error"}

        except Exception:
            # Log any other exceptions
            logger.error("Error fetching current user:\n%s", traceback.format_exc())
            return {"error": "Internal server error"}

# ---------------------------- Service Instance ----------------------------
# Singleton instance for reuse in auth routes
current_user_handler = CurrentUserHandler()
