# ---------------------------- External Imports ----------------------------

# Import SQLAlchemy column types and helper functions
from sqlalchemy import Column, Integer, String, DateTime, Boolean

# Import SQL function helpers (e.g., func.now() for timestamps)
from sqlalchemy.sql import func


# ---------------------------- Internal Imports ----------------------------

# Import async declarative base for model inheritance
from ...database.base import Base


# ---------------------------- Admin Model ----------------------------

# Define Admin table for admin users
class Admin(Base):
    """
    Admin table for storing user credentials and metadata.
    Tokens are not stored here — see AdminToken table for multi-login support.
    """
    __tablename__ = "admin"

    # ---------------------------- Columns ----------------------------

    # Unique internal ID (primary key)
    id = Column(Integer, primary_key=True, index=True)

    # Full name of the admin
    name = Column(String, nullable=False)

    # Email used for login (must be unique)
    email = Column(String, unique=True, index=True, nullable=False)

    # Hashed password; nullable for OAuth2 users who don't set a password
    hashed_password = Column(String, nullable=True)

    # Account verification flag (true if email verified)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Timestamp when record was created
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Timestamp when record was last updated (auto-updates on modification)
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False
    )
