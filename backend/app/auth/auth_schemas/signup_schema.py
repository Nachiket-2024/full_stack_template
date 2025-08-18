# ---------------------------- External Imports ----------------------------
# Pydantic for request validation
from pydantic import BaseModel, EmailStr

# ---------------------------- Signup Schema ----------------------------
class SignupSchema(BaseModel):
    """
    Schema for signup requests.
    """
    name: str                           # Full name
    email: EmailStr                     # Email address
    password: str                       # Plain password, will be hashed
