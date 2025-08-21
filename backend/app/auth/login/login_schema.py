# ---------------------------- External Imports ----------------------------
# Import Pydantic's BaseModel for schema creation and EmailStr for email validation
from pydantic import BaseModel, EmailStr

# ---------------------------- Login Schema ----------------------------
class LoginSchema(BaseModel):
    """
    Schema for login requests.
    Defines the required fields for user login input validation.
    """
    
    # User's email address (validated to ensure proper email format)
    email: EmailStr
    
    # User's plain text password (will be verified against stored hash in service layer)
    password: str
