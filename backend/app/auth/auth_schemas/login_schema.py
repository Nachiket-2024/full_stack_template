# ---------------------------- External Imports ----------------------------
# Pydantic for request validation
from pydantic import BaseModel, EmailStr

# ---------------------------- Login Schema ----------------------------
class LoginSchema(BaseModel):
    """
    Schema for login requests.
    """
    email: EmailStr                     # Email address
    password: str                       # Plain password for verification
