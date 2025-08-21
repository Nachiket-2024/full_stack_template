# ---------------------------- External Imports ----------------------------

# Import BaseModel for Pydantic schemas and ConfigDict for ORM configuration
from pydantic import BaseModel, ConfigDict

# Import datetime for timestamp fields
from datetime import datetime


# ---------------------------- Base Token Schema ----------------------------

# Base schema containing shared fields for Admin tokens
class AdminTokenBase(BaseModel):
    """
    Shared fields for Admin token records.
    """
    # Access token string
    access_token: str

    # Refresh token string
    refresh_token: str


# ---------------------------- Schema for Token Creation ----------------------------

# Schema for creating new AdminToken entries in the database
class AdminTokenCreate(AdminTokenBase):
    """
    Fields required when creating a new token record.
    """
    # Optional creation timestamp (can default to DB-generated)
    created_at: datetime = None

    # Optional last updated timestamp (can default to DB-generated)
    updated_at: datetime = None


# ---------------------------- Schema for Reading Tokens ----------------------------

# Schema for reading AdminToken records from the database
class AdminTokenRead(AdminTokenBase):
    """
    Fields returned when reading token records from the DB.
    """
    # Unique ID of the token record
    id: int

    # Timestamp when token record was created
    created_at: datetime

    # Timestamp of last update to the token record
    updated_at: datetime

    class Config(ConfigDict):
        # Enable reading from SQLAlchemy ORM objects
        from_attributes = True
