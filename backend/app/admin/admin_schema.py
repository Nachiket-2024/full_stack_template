# ---------------------------- External Imports ----------------------------
from pydantic import BaseModel, EmailStr, ConfigDict
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

# ---------------------------- Schema for Update ----------------------------
class AdminUpdate(BaseModel):
    """
    Fields allowed to update for Admin user.
    All fields default to None for partial updates.
    """
    name: str = None
    password: str = None  # Will be hashed if provided

# ---------------------------- Schema for Reading ----------------------------
class AdminRead(AdminBase):
    """
    Fields returned in API responses.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config(ConfigDict):
        from_attributes = True  # Enable ORM objects (SQLAlchemy models) to be converted to Pydantic
