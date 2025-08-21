# ---------------------------- External Imports ----------------------------

# Import SQLAlchemy column types and ForeignKey support
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey

# Import SQL function helpers (e.g., func.now() for timestamps)
from sqlalchemy.sql import func


# ---------------------------- Internal Imports ----------------------------

# Import async declarative base for model inheritance
from ...database.base import Base


# ---------------------------- AdminToken Model ----------------------------

# Table to store multiple login sessions for Admin users
class AdminToken(Base):
    """
    Stores multiple access and refresh tokens per Admin user.
    Each login session creates a new row to support concurrent sessions.
    """
    __tablename__ = "admin_token"

    # ---------------------------- Columns ----------------------------

    # Unique internal ID for this token row
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key reference to Admin table
    admin_id = Column(Integer, ForeignKey("admin.id"), nullable=False)

    # Access token for authentication
    access_token = Column(String, nullable=False)

    # Refresh token to obtain new access tokens
    refresh_token = Column(String, nullable=False)

    # Optional metadata about the device/browser used
    device_info = Column(String, nullable=True)

    # Indicates if the session is active
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamp when this token row was created
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Optional timestamp when token expires
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamp for last update (auto-updates on modification)
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False
    )
