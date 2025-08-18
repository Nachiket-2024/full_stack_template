# ---------------------------- External Imports ----------------------------
# Password hashing library
from passlib.context import CryptContext

# For datetime calculations
from datetime import datetime, timedelta

# JWT encoding/decoding
import jwt

# ---------------------------- Internal Imports ----------------------------
# Load settings like SECRET_KEY from core
from ...core.settings import settings

# ---------------------------- Password Context ----------------------------
# Context for hashing passwords using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------- Password Service ----------------------------
class PasswordService:
    """
    Service to handle password hashing, verification, and reset tokens.
    """

    # ---------------------------- Hash Password ----------------------------
    # Input: plain text password
    # Output: hashed password string
    @staticmethod
    async def hash_password(password: str) -> str:
        """
        Hash plain password asynchronously.
        """
        return pwd_context.hash(password)

    # ---------------------------- Verify Password ----------------------------
    # Input: plain password, hashed password
    # Output: True if match, False otherwise
    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against the stored hash.
        """
        return pwd_context.verify(plain_password, hashed_password)

    # ---------------------------- Validate Password Strength ----------------------------
    # Input: plain password
    # Output: True if strong, False otherwise
    @staticmethod
    async def validate_password_strength(password: str) -> bool:
        """
        Check password strength: minimum 8 chars, at least one number, one symbol.
        """
        import re
        if len(password) < 8:
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    # ---------------------------- Create Reset Token ----------------------------
    # Input: user email, table name, expiration in minutes
    # Output: JWT token string
    @staticmethod
    async def create_reset_token(email: str, table_name: str, expires_minutes: int = 15) -> str:
        """
        Generate a short-lived JWT for password reset.
        """
        # Calculate expiration timestamp
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)

        # Prepare payload with minimal info
        payload: dict[str, str | float] = {
            "sub": email,          # Subject: user's email
            "table": table_name,   # Table name for role-specific user
            "exp": expire.timestamp()  # Expiration timestamp
        }

        # Encode JWT
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token

    # ---------------------------- Verify Reset Token ----------------------------
    # Input: JWT token string
    # Output: payload dict if valid, None if invalid/expired
    @staticmethod
    async def verify_reset_token(token: str) -> dict | None:
        """
        Verify reset token. Returns payload if valid, None otherwise.
        """
        try:
            # Decode JWT
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            # Token expired
            return None
        except jwt.InvalidTokenError:
            # Invalid token
            return None

# ---------------------------- Service Instance ----------------------------
# Single instance for global use
password_service = PasswordService()
