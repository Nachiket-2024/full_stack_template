# ---------------------------- External Imports ----------------------------
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs


# ---------------------------- Base ----------------------------
# Use AsyncAttrs for async support in models
Base = declarative_base(cls=AsyncAttrs)
