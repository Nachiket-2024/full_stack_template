# ---------------------------- External Imports ----------------------------
# Import BaseModel for schema definitions and ConfigDict for ORM config
from pydantic import BaseModel, ConfigDict

# Import datetime for timestamp fields
from datetime import datetime

# ---------------------------- Base Token Schema ----------------------------
# Define base schema containing shared fields for Role1 token records
class Role1TokenBase(BaseModel):
    """
    Shared fields for Role1 token records.
    """

    # Define email of the Role1 user (FK reference)
    email: str

    # Define access token string
    access_token: str

    # Define refresh token string
    refresh_token: str

# ---------------------------- Schema for Token Creation ----------------------------
# Define schema for creating a new token record, inheriting from Role1TokenBase
class Role1TokenCreate(Role1TokenBase):
    """
    Fields required when creating a new token record.
    """

    # Define optional creation timestamp (defaults to DB-generated if not provided)
    created_at: datetime | None = None

# ---------------------------- Schema for Reading Tokens ----------------------------
# Define schema for reading token records from the DB, inheriting from Role1TokenBase
class Role1TokenRead(Role1TokenBase):
    """
    Fields returned when reading token records from the DB.
    """

    # Define unique ID of the token record
    id: int

    # Define timestamp when token record was created
    created_at: datetime

    # Configure schema to allow loading from ORM objects
    class Config(ConfigDict):
        # Enable reading attributes directly from ORM models
        from_attributes = True
