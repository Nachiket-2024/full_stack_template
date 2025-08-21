# ---------------------------- External Imports ----------------------------
# Import BaseModel for data validation and type enforcement
# Import EmailStr to ensure proper email format validation
from pydantic import BaseModel, EmailStr

# ---------------------------- Signup Schema ----------------------------
# Define a Pydantic model for signup requests
class SignupSchema(BaseModel):
    """
    Schema for signup requests.
    """

    # User's full name as a string
    name: str

    # User's email address, validated against standard email format
    email: EmailStr

    # Plain password (to be validated and hashed later)
    password: str
