# ---------------------------- External Imports ----------------------------
# Pydantic for request validation
from pydantic import BaseModel, EmailStr

# ---------------------------- Password Reset Request Schema ----------------------------
class PasswordResetRequestSchema(BaseModel):
    """
    Schema for requesting password reset.
    """
    email: EmailStr                     # Email address to send reset token
