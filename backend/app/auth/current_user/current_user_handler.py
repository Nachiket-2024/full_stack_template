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

# Role mapping for querying user based on role
from ...access_control.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Current User Handler Class ----------------------------
# Handles fetching the currently authenticated user
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
            3. Extract user email and role from token payload.
            4. Validate email and role values.
            5. Get the appropriate CRUD instance for the user's role.
            6. Query the database for the user by email.
            7. Return basic user information if found, else raise exception.

        Output:
            1. dict: Contains user info ('name', 'email', 'role') if successful.
        """
        try:
            # Step 1: Check if access token is provided
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No access token provided"
                )

            # Step 2: Verify the access token using JWT service
            payload = await jwt_service.verify_token(access_token)

            # Raise error if invalid or expired token
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )

            # Step 3: Extract user email and role from token payload
            email = payload.get("email")
            role = payload.get("role")

            # Step 4: Validate email and role values
            if not email or not role:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )

            # Step 5: Get the appropriate CRUD instance for the user's role
            crud_instance = ROLE_TABLES.get(role)

            # Step 5 (continued): Raise error if no valid role found
            if not crud_instance:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User role not recognized"
                )

            # Step 6: Query the database for the user by email
            user = await crud_instance.get_by_email(email, db)

            # Step 6 (continued): Raise error if user not found
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            # Step 7: Return basic user information if found, else raise exception
            return {
                "name": getattr(user, "name", "Unknown"),
                "email": getattr(user, "email", None),
                "role": role
            }

        # Handle database errors
        except SQLAlchemyError:
            logger.error("Database error fetching current user:\n%s", traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )

        # Re-raise known HTTPExceptions
        except HTTPException:
            raise

        # Handle unexpected errors
        except Exception:
            logger.error("Error fetching current user:\n%s", traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )


# ---------------------------- Service Instance ----------------------------
# Singleton instance of CurrentUserHandler
current_user_handler = CurrentUserHandler()
