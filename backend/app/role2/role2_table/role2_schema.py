# ---------------------------- External Imports ----------------------------
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

# ---------------------------- Base Schema ----------------------------
class Role2Base(BaseModel):
    """
    Shared fields for Role2 users.
    """
    name: str
    email: EmailStr

# ---------------------------- Schema for Creation ----------------------------
class Role2Create(Role2Base):
    """
    Fields required when creating a new Role2 user.
    """
    password: str  # Plain password, will be hashed before saving
    is_verified: bool = False  # Default to False until email verification

# ---------------------------- Schema for Update ----------------------------
class Role2Update(BaseModel):
    """
    Fields allowed to update for Role2 user.
    All fields default to None for partial updates.
    """
    name: str = None
    password: str = None  # Will be hashed if provided
    is_verified: bool = None  # Can update verification status

# ---------------------------- Schema for Reading ----------------------------
class Role2Read(Role2Base):
    """
    Fields returned in API responses.
    """
    id: int
    created_at: datetime
    updated_at: datetime
    is_verified: bool  # Include verification status

    class Config(ConfigDict):
        from_attributes = True  # Enable ORM objects (SQLAlchemy models) to be converted to Pydantic
