# ---------------------------- External Imports ----------------------------
# Import BaseModel for schema definitions and ConfigDict for ORM config
from pydantic import BaseModel, ConfigDict

# Import datetime for timestamp fields
from datetime import datetime

# ---------------------------- Base Token Schema ----------------------------
# Define base schema containing shared fields for Admin token records
class AdminTokenBase(BaseModel):
    """
    Shared fields for Admin token records.
    """

    # Define email of the Admin user (FK reference)
    email: str

    # Define access token string
    access_token: str

    # Define refresh token string
    refresh_token: str

# ---------------------------- Schema for Token Creation ----------------------------
# Define schema for creating a new token record, inheriting from AdminTokenBase
class AdminTokenCreate(AdminTokenBase):
    """
    Fields required when creating a new token record.
    """

    # Define optional creation timestamp (defaults to DB-generated if not provided)
    created_at: datetime | None = None

# ---------------------------- Schema for Reading Tokens ----------------------------
# Define schema for reading token records from the DB, inheriting from AdminTokenBase
class AdminTokenRead(AdminTokenBase):
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
