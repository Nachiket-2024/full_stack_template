# ---------------------------- External Imports ----------------------------
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

# ---------------------------- Internal Imports ----------------------------
from ..database.base import Base  # Async declarative base

# ---------------------------- Role2 Model ----------------------------
class Role1(Base):
    """
    Role2 table for storing role2 user credentials and metadata,
    now including account verification status.
    """
    __tablename__ = "role1"

    # ---------------------------- Columns ----------------------------
    id = Column(Integer, primary_key=True, index=True)                  # Unique internal ID
    name = Column(String, nullable=False)                               # Full name
    email = Column(String, unique=True, index=True, nullable=False)     # Login identifier
    hashed_password = Column(String, nullable=True)                     # Password hash (nullable for OAuth2)
    access_token = Column(String, nullable=True)                        # Optional access token
    refresh_token = Column(String, nullable=True)                       # Optional refresh token
    is_verified = Column(Boolean, default=False, nullable=False)        # Account verification status
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Creation timestamp
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)  # Last update
