# ---------------------------- External Imports ----------------------------
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

# ---------------------------- Base Schema ----------------------------
class Role1Base(BaseModel):
    """
    Shared fields for Role1 users.
    """
    name: str
    email: EmailStr

# ---------------------------- Schema for Creation ----------------------------
class Role1Create(Role1Base):
    """
    Fields required when creating a new Role1 user.
    """
    password: str  # Plain password, will be hashed before saving

# ---------------------------- Schema for Update ----------------------------
class Role1Update(BaseModel):
    """
    Fields allowed to update for Role1 user.
    All fields default to None for partial updates.
    """
    name: str = None
    password: str = None  # Will be hashed if provided

# ---------------------------- Schema for Reading ----------------------------
class Role1Read(Role1Base):
    """
    Fields returned in API responses.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config(ConfigDict):
        from_attributes = True  # Enable ORM objects (SQLAlchemy models) to be converted to Pydantic
