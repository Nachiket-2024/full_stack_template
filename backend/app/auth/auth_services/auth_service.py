# ---------------------------- External Imports ----------------------------
# For logging and traceback
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Database CRUDs for roles
from ...role1.role1_crud import role1_crud
from ...role2.role2_crud import role2_crud
from ...admin.admin_crud import admin_crud

# Password service for hashing and verification
from .password_service import password_service

# JWT service for token generation
from .jwt_service import jwt_service

# Login protection for brute-force prevention
from ..auth_security.login_protection_service import login_protection_service

# ---------------------------- Logger Setup ----------------------------
# Configure logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Auth Service ----------------------------
class AuthService:
    """
    Service to handle email/password login, signup,
    default role assignment, and JWT token issuance.
    Includes brute-force login protection.
    """

    # ---------------------------- Signup ----------------------------
    @staticmethod
    async def signup(name: str, email: str, password: str) -> dict | None:
        """
        Sign up a new user with default role2.
        Returns JWT access & refresh tokens on success.
        """
        try:
            # Validate password strength
            if not await password_service.validate_password_strength(password):
                logger.warning("Weak password during signup for email: %s", email)
                return None

            # Check if user exists in any role
            for crud in [admin_crud, role1_crud, role2_crud]:
                existing_user = await crud.get_by_email(email)
                if existing_user:
                    logger.info("Signup attempt with existing email: %s", email)
                    return None  # User already exists

            # Hash password
            hashed_password = await password_service.hash_password(password)

            # Assign role2 by default
            user_data = {"name": name, "email": email, "hashed_password": hashed_password}
            _ = await role2_crud.create(user_data)

            # Generate JWT tokens
            access_token = await jwt_service.create_access_token(email, "role2")
            refresh_token = await jwt_service.create_refresh_token(email, "role2")
            return {"access_token": access_token, "refresh_token": refresh_token}

        except Exception:
            logger.error("Error during signup:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Login ----------------------------
    @staticmethod
    async def login(email: str, password: str, ip_address: str) -> dict | None:
        """
        Login user by email/password.
        Returns JWT access & refresh tokens on success.
        Implements brute-force protection for both email and IP.
        """
        try:
            # Define Redis keys for email and IP
            email_lock_key = f"login_lock:email:{email}"
            ip_lock_key = f"login_lock:ip:{ip_address}"

            # Check if account or IP is locked
            if await login_protection_service.is_locked(email_lock_key):
                logger.warning("Login attempt for locked account: %s", email)
                return None
            if await login_protection_service.is_locked(ip_lock_key):
                logger.warning("Login attempt from locked IP: %s", ip_address)
                return None

            # Find user in all roles
            for role, crud in [("admin", admin_crud), ("role1", role1_crud), ("role2", role2_crud)]:
                user = await crud.get_by_email(email)
                if user:
                    user_role = role
                    _ = crud
                    break
            else:
                # Record failed attempts for both email and IP
                await login_protection_service.record_failed_attempt(email_lock_key)
                await login_protection_service.record_failed_attempt(ip_lock_key)
                logger.info("Login attempt with non-existing email: %s from IP: %s", email, ip_address)
                return None  # User not found

            # Verify password
            if not await password_service.verify_password(password, user.hashed_password):
                # Record failed attempts for both email and IP
                await login_protection_service.record_failed_attempt(email_lock_key)
                await login_protection_service.record_failed_attempt(ip_lock_key)
                logger.warning("Incorrect password for email: %s from IP: %s", email, ip_address)
                return None

            # Reset failed attempts on successful login
            await login_protection_service.reset_failed_attempts(email_lock_key)
            await login_protection_service.reset_failed_attempts(ip_lock_key)

            # Generate JWT tokens
            access_token = await jwt_service.create_access_token(email, user_role)
            refresh_token = await jwt_service.create_refresh_token(email, user_role)
            return {"access_token": access_token, "refresh_token": refresh_token}

        except Exception:
            logger.error("Error during login:\n%s", traceback.format_exc())
            return None


# ---------------------------- Service Instance ----------------------------
# Single instance for global use
auth_service = AuthService()
