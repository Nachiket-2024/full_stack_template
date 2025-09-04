# ---------------------------- External Imports ----------------------------
# Pydantic for request validation
from pydantic import BaseModel, EmailStr

# ---------------------------- Password Reset Request Schema ----------------------------
class PasswordResetRequestSchema(BaseModel):

    email: EmailStr                     # Email address to send reset token
