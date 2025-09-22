# ---------------------------- External Imports ----------------------------
# Import BaseModel for schema definitions, ConfigDict for ORM config, EmailStr for validated email field
from pydantic import BaseModel, ConfigDict, EmailStr  

# Import datetime for timestamp fields
from datetime import datetime  

# ---------------------------- Base Schema ----------------------------
class AdminBase(BaseModel):
    """
    Shared fields for Admin users.
    """
    name: str
    email: EmailStr

# ---------------------------- Schema for Creation ----------------------------
class AdminCreate(AdminBase):
    """
    Fields required when creating a new Admin user.
    """
    password: str  # Plain password, will be hashed before saving
    is_verified: bool = False  # Default to False until email verification

# ---------------------------- Schema for Update ----------------------------
class AdminUpdate(BaseModel):
    """
    Fields allowed to update for Admin user.
    All fields default to None for partial updates.
    """
    name: str = None
    password: str = None  # Will be hashed if provided
    is_verified: bool = None  # Can update verification status

# ---------------------------- Schema for Reading ----------------------------
class AdminRead(AdminBase):
    """
    Fields returned in API responses.
    """
    id: int
    created_at: datetime
    updated_at: datetime
    is_verified: bool  # Include verification status

    class Config(ConfigDict):
        from_attributes = True  # Enable ORM objects (SQLAlchemy models) to be converted to Pydantic
