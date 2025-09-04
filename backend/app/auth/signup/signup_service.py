# ---------------------------- External Imports ----------------------------
# Logging for tracking events, warnings, and errors during signup
import logging

# Capture full exception stack traces for debugging
import traceback

# Async SQLAlchemy session for database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Role-based CRUD tables and default role for assigning new users
from ...access_control.role_tables import ROLE_TABLES, DEFAULT_ROLE

# Password service for hashing passwords and validating strength
from ..password_logic.password_service import password_service

# ---------------------------- Logger Setup ----------------------------
# Configure module-specific logger for structured logging
logger = logging.getLogger(__name__)

# ---------------------------- Signup Service ----------------------------
# Service class to handle user signup logic
class SignupService:

    # ---------------------------- Static Async Signup Method ----------------------------
    # Static async method to create a new user
    @staticmethod
    async def signup(name: str, email: str, password: str, role: str | None = None, db: AsyncSession = None) -> bool:
        
        try:
            # ---------------------------- Validate Password Strength ----------------------------
            # Check if password meets security requirements
            if not await password_service.validate_password_strength(password):
                logger.warning("Weak password during signup for email: %s", email)
                return False

            # ---------------------------- Check for Existing Users ----------------------------
            # Iterate over all roles to check if email is already registered
            for crud in ROLE_TABLES.values():
                if await crud.get_by_email(email, db=db):
                    logger.info("Signup attempt with existing email: %s", email)
                    return False

            # ---------------------------- Hash Password ----------------------------
            # Hash the password securely before storing
            hashed_password = await password_service.hash_password(password)

            # Assign role or fallback to default role
            role = role or DEFAULT_ROLE

            # Validate role exists in role tables
            if role not in ROLE_TABLES:
                logger.warning("Invalid role during signup: %s", role)
                return False

            # ---------------------------- Create User ----------------------------
            # Prepare user data dictionary
            user_data = {
                "name": name,
                "email": email,
                "hashed_password": hashed_password,
                "is_verified": False  # New users start unverified
            }

            # Create user in DB using the appropriate role table
            await ROLE_TABLES[role].create(user_data, db=db)  # pass async session
            logger.info("User %s created with role %s", email, role)
            return True

        except Exception:
            # Log any exception with full traceback
            logger.error("Error during signup:\n%s", traceback.format_exc())
            return False


# ---------------------------- Instantiate SignupService ----------------------------
# Singleton instance to handle signup operations
signup_service = SignupService()
