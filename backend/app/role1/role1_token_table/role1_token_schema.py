# ---------------------------- External Imports ----------------------------

# Import BaseModel for Pydantic schemas and ConfigDict for ORM configuration
from pydantic import BaseModel, ConfigDict

# Import datetime for timestamp fields
from datetime import datetime


# ---------------------------- Base Token Schema ----------------------------

# Base schema containing shared fields for Role1 tokens
class Role1TokenBase(BaseModel):
    """
    Shared fields for Role1 token records.
    """
    # Access token string
    access_token: str

    # Refresh token string
    refresh_token: str


# ---------------------------- Schema for Token Creation ----------------------------

# Schema for creating new Role1Token entries in the database
class Role1TokenCreate(Role1TokenBase):
    """
    Fields required when creating a new Role1 token record.
    """
    # Optional creation timestamp (can be set by DB)
    created_at: datetime = None

    # Optional last updated timestamp (can be set by DB)
    updated_at: datetime = None


# ---------------------------- Schema for Reading Tokens ----------------------------

# Schema for reading Role1Token records from the database
class Role1TokenRead(Role1TokenBase):
    """
    Fields returned when reading Role1 token records from the DB.
    """
    # Unique ID of the token record
    id: int

    # Timestamp when token record was created
    created_at: datetime

    # Timestamp of last update to the token record
    updated_at: datetime

    # Enable ORM reading from SQLAlchemy models using from_attributes
    class Config(ConfigDict):
        from_attributes = True
