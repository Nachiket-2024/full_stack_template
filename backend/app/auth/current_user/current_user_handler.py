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
# Create a logger instance specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Current User Handler Class ----------------------------
# Handler class to manage fetching the currently authenticated user
class CurrentUserHandler:
    """
    1. get_current_user - Fetch the currently authenticated user's basic information.
    """

    # ---------------------------- Get Current User ----------------------------
    # Async method to fetch the current user from DB using access token
    async def get_current_user(self, access_token: str, db) -> dict | None:
        """
        Input:
            1. access_token (str): JWT token provided by the client.
            2. db: Database session for querying user records.

        Process:
            1. Check if access token is provided.
            2. Verify the access token using JWT service.
            3. Extract user email and table (role) from token payload.
            4. Validate email and table values.
            5. Get the appropriate CRUD instance for the user's role/table.
            6. Query the database for the user by email.
            7. Return basic user information if found.

        Output:
            1. dict: Contains user info ('name', 'email', 'table') if successful,
                     or an 'error' key with a message if unsuccessful.
        """
        try:
            # ---------------------------- Validate Token ----------------------------
            # Return error if no token is provided
            if not access_token:
                return {"error": "No access token provided"}

            # ---------------------------- Verify Token ----------------------------
            # Verify token using JWT service
            payload = await jwt_service.verify_token(access_token)
            # Return error if token is invalid or expired
            if not payload:
                return {"error": "Invalid or expired token"}

            # ---------------------------- Extract User Info ----------------------------
            # Extract email and table (role) from token payload
            email = payload.get("email")
            table = payload.get("table")
            # Return error if email or table is missing
            if not email or not table:
                return {"error": "Invalid token payload"}

            # ---------------------------- Get CRUD Instance ----------------------------
            # Get corresponding CRUD instance for the user's role/table
            crud_instance = ROLE_TABLES.get(table)
            # Return error if no CRUD instance found for the role/table
            if not crud_instance:
                return {"error": "User table/role not found"}

            # ---------------------------- Fetch User from DB ----------------------------
            # Query database for user by email
            user = await crud_instance.get_by_email(db, email)
            # Return error if user not found
            if not user:
                return {"error": "User not found"}

            # ---------------------------- Return User Info ----------------------------
            # Return user's basic info
            return {
                "name": getattr(user, "name", "Unknown"),
                "email": getattr(user, "email", None),
                "table": table
            }

        # ---------------------------- Exception Handling: Database Errors ----------------------------
        # Handle SQLAlchemy database errors
        except SQLAlchemyError:
            logger.error("Database error fetching current user:\n%s", traceback.format_exc())
            return {"error": "Database error"}

        # ---------------------------- Exception Handling: General Errors ----------------------------
        # Handle any other unexpected errors
        except Exception:
            logger.error("Error fetching current user:\n%s", traceback.format_exc())
            return {"error": "Internal server error"}


# ---------------------------- Service Instance ----------------------------
# Singleton instance for reuse in authentication routes
current_user_handler = CurrentUserHandler()
