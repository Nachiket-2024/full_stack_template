# ---------------------------- External Imports ----------------------------
# Pydantic for request validation
from pydantic import BaseModel

# ---------------------------- Password Reset Schema ----------------------------
class PasswordResetConfirmSchema(BaseModel):
    """
    Schema for confirming password reset using token.
    """
    token: str                          # JWT reset token
    new_password: str                   # New password to set
