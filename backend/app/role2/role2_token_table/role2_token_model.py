# ---------------------------- External Imports ----------------------------
# Import Column, String, DateTime, Boolean, ForeignKey, and Integer for defining SQLAlchemy model fields
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer

# Import func for SQL functions like now()
from sqlalchemy.sql import func

# ---------------------------- Internal Imports ----------------------------
# Import Base class for declarative model definitions
from ...database.base import Base

# ---------------------------- Role2Token Model ----------------------------
# Define Role2Token model extending Base (SQLAlchemy ORM model)
class Role2Token(Base):
    """
    Stores multiple access and refresh tokens per Role2 user.
    Uses email as FK reference to Role2 table (unique identifier).
    """

    # Set table name for this model
    __tablename__ = "role2_token"

    # Define unique internal ID as primary key with index
    id = Column(Integer, primary_key=True, index=True)

    # Define foreign key linking email field to Role2 table
    email = Column(String, ForeignKey("role2.email"), nullable=False, index=True)

    # Define access token field (required)
    access_token = Column(String, nullable=False)

    # Define refresh token field (required)
    refresh_token = Column(String, nullable=False)

    # Define optional field to store device/browser information
    device_info = Column(String, nullable=True)

    # Define creation timestamp with default value as current time
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
