# ---------------------------- External Imports ----------------------------
# For logging errors and traceback
import logging
import traceback
import asyncio  # For concurrent async calls

# ---------------------------- Internal Imports ----------------------------
# Centralized role table CRUDs and default role
from ...core.role_tables import ROLE_TABLES, DEFAULT_ROLE

# Password service for hashing and verification
from .password_service import password_service

# JWT service for token generation
from .jwt_service import jwt_service

# Login protection for brute-force prevention
from ..auth_security.login_protection_service import login_protection_service

# Schema for standardized token responses (access + refresh pair)
from ..auth_schemas.refresh_token_schema import TokenPairResponseSchema

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
    async def signup(name: str, email: str, password: str, role: str | None = None) -> TokenPairResponseSchema | None:
        """
        Sign up a new user.
        - Uses DEFAULT_ROLE if no role is provided.
        Returns JWT access & refresh tokens on success.
        """
        try:
            # ---------------------------- Validate Password ----------------------------
            if not await password_service.validate_password_strength(password):
                logger.warning("Weak password during signup for email: %s", email)
                return None

            # ---------------------------- Check if User Exists in Any Role ----------------------------
            for crud in ROLE_TABLES.values():
                if await crud.get_by_email(email):
                    logger.info("Signup attempt with existing email: %s", email)
                    return None

            # ---------------------------- Hash Password ----------------------------
            hashed_password = await password_service.hash_password(password)

            # ---------------------------- Assign Role ----------------------------
            role = role or DEFAULT_ROLE
            if role not in ROLE_TABLES:
                logger.warning("Attempt to create user with invalid role: %s", role)
                return None

            # ---------------------------- Create User ----------------------------
            user_data = {"name": name, "email": email, "hashed_password": hashed_password}
            await ROLE_TABLES[role].create(user_data)
            logger.info("User %s created with role %s", email, role)

            # ---------------------------- Generate JWT Tokens ----------------------------
            access_token, refresh_token = await asyncio.gather(
                jwt_service.create_access_token(email, role),
                jwt_service.create_refresh_token(email, role)
            )

            # ---------------------------- Store Tokens in DB ----------------------------
            await ROLE_TABLES[role].update_by_email(email, {
                "access_token": access_token,
                "refresh_token": refresh_token
            })

            # ---------------------------- Return Tokens via Schema ----------------------------
            return TokenPairResponseSchema(access_token=access_token, refresh_token=refresh_token)

        except Exception:
            logger.error("Error during signup:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Login ----------------------------
    @staticmethod
    async def login(email: str, password: str, ip_address: str) -> TokenPairResponseSchema | None:
        """
        Login user by email/password.
        Returns JWT access & refresh tokens on success.
        Implements brute-force protection for both email and IP.
        """
        try:
            email_lock_key = f"login_lock:email:{email}"
            ip_lock_key = f"login_lock:ip:{ip_address}"

            # ---------------------------- Check Locks Concurrently ----------------------------
            email_locked, ip_locked = await asyncio.gather(
                login_protection_service.is_locked(email_lock_key),
                login_protection_service.is_locked(ip_lock_key)
            )
            if email_locked:
                logger.warning("Login attempt for locked account: %s", email)
                return None
            if ip_locked:
                logger.warning("Login attempt from locked IP: %s", ip_address)
                return None

            # ---------------------------- Find User ----------------------------
            user = None
            user_role = None
            for role_name, crud in ROLE_TABLES.items():
                user = await crud.get_by_email(email)
                if user:
                    user_role = role_name
                    break

            # ---------------------------- Handle Non-existing User ----------------------------
            if not user:
                await asyncio.gather(
                    login_protection_service.record_failed_attempt(email_lock_key),
                    login_protection_service.record_failed_attempt(ip_lock_key)
                )
                logger.info("Login attempt with non-existing email: %s from IP: %s", email, ip_address)
                return None

            # ---------------------------- Verify Password ----------------------------
            if not await password_service.verify_password(password, user.hashed_password):
                await asyncio.gather(
                    login_protection_service.record_failed_attempt(email_lock_key),
                    login_protection_service.record_failed_attempt(ip_lock_key)
                )
                logger.warning("Incorrect password for email: %s from IP: %s", email, ip_address)
                return None

            # ---------------------------- Reset Failed Attempts ----------------------------
            await asyncio.gather(
                login_protection_service.reset_failed_attempts(email_lock_key),
                login_protection_service.reset_failed_attempts(ip_lock_key)
            )

            # ---------------------------- Generate JWT Tokens ----------------------------
            access_token, refresh_token = await asyncio.gather(
                jwt_service.create_access_token(email, user_role),
                jwt_service.create_refresh_token(email, user_role)
            )

            # ---------------------------- Store Tokens in DB ----------------------------
            await ROLE_TABLES[user_role].update_by_email(email, {
                "access_token": access_token,
                "refresh_token": refresh_token
            })

            # ---------------------------- Return Tokens via Schema ----------------------------
            return TokenPairResponseSchema(access_token=access_token, refresh_token=refresh_token)

        except Exception:
            logger.error("Error during login:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Mark User Verified ----------------------------
    @staticmethod
    async def mark_user_verified(email: str) -> bool:
        """
        Mark a user as verified in the first role table where they exist.
        Returns True if updated, False if user not found or already verified.
        """
        try:
            for role_name, crud in ROLE_TABLES.items():
                user = await crud.get_by_email(email)
                if user and not getattr(user, "is_verified", False):
                    await crud.update_by_email(email, {"is_verified": True})
                    logger.info("User %s marked as verified in table %s", email, role_name)
                    return True
            return False
        except Exception:
            logger.error("Error marking user verified:\n%s", traceback.format_exc())
            return False


# ---------------------------- Service Instance ----------------------------
auth_service = AuthService()
