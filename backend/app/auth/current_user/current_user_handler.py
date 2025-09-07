# ---------------------------- External Imports ----------------------------
# Logging module for tracking errors and events
import logging

# Module to capture full stack traces for debugging exceptions
import traceback

# SQLAlchemy exceptions for handling DB errors
from sqlalchemy.exc import SQLAlchemyError

# FastAPI HTTP exception for proper status codes
from fastapi import HTTPException, status

# ---------------------------- Internal Imports ----------------------------
# JWT service to decode and verify access tokens
from ..token_logic.jwt_service import jwt_service

# Role tables for querying user based on role
from ...access_control.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Current User Handler Class ----------------------------
class CurrentUserHandler:
    """
    1. get_current_user - Fetch the currently authenticated user's basic information.
    """

    # ---------------------------- Get Current User ----------------------------
    async def get_current_user(self, access_token: str, db) -> dict:
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
            7. Return basic user information if found, else raise exception.

        Output:
            1. dict: Contains user info ('name', 'email', 'table') if successful.
        """
        try:
            # ---------------------------- Validate Token ----------------------------
            # Ensure token is provided
            if not access_token:
                # Raise HTTP 401 if no token
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No access token provided"
                )

            # ---------------------------- Verify Token ----------------------------
            # Decode and verify token payload
            payload = await jwt_service.verify_token(access_token)
            if not payload:
                # Raise HTTP 401 if invalid or expired
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )

            # ---------------------------- Extract User Info ----------------------------
            # Extract user email and role table from payload
            email = payload.get("email")
            table = payload.get("table")
            if not email or not table:
                # Raise HTTP 401 if payload missing required fields
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )

            # ---------------------------- Get CRUD Instance ----------------------------
            # Retrieve role-specific CRUD instance
            crud_instance = ROLE_TABLES.get(table)
            if not crud_instance:
                # Raise HTTP 401 if no valid role/table found
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User table/role not found"
                )

            # ---------------------------- Fetch User from DB ----------------------------
            # Query database for user record
            user = await crud_instance.get_by_email(db, email)
            if not user:
                # Raise HTTP 401 if user not found in DB
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            # ---------------------------- Return User Info ----------------------------
            # Return dictionary with basic user information
            return {
                "name": getattr(user, "name", "Unknown"),
                "email": getattr(user, "email", None),
                "table": table
            }

        # ---------------------------- Handle DB Errors ----------------------------
        except SQLAlchemyError:
            # Log DB error with traceback
            logger.error("Database error fetching current user:\n%s", traceback.format_exc())
            # Raise HTTP 500 for DB issues
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )

        # ---------------------------- Handle Known HTTP Errors ----------------------------
        except HTTPException:
            # Re-raise known HTTPExceptions to preserve status codes
            raise

        # ---------------------------- Handle Other Errors ----------------------------
        except Exception:
            # Log unexpected error with traceback
            logger.error("Error fetching current user:\n%s", traceback.format_exc())
            # Raise HTTP 500 for generic internal server error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )


# ---------------------------- Service Instance ----------------------------
# Singleton instance of CurrentUserHandler
current_user_handler = CurrentUserHandler()
