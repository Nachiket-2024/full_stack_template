# ---------------------------- External Imports ----------------------------
# Import SQLAlchemy async engine creator and AsyncSession type
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Import sessionmaker to create session factory for async sessions
from sqlalchemy.orm import sessionmaker

# ---------------------------- Settings Import ----------------------------
# Import application settings (contains DATABASE_URL, etc.)
from ..core.settings import settings

# ---------------------------- Async Engine ----------------------------
# Database class to encapsulate async engine and session creation
class Database:
    # ---------------------------- Initialization ----------------------------
    def __init__(self, database_url: str):
        # Store the database URL
        self.database_url = database_url
        # Create an asynchronous SQLAlchemy engine
        self.engine = create_async_engine(
            self.database_url,
            echo=True  # Enable SQL query logging for debugging
        )
        # Create a session factory bound to the async engine
        self.async_session = sessionmaker(
            bind=self.engine,          # Bind sessions to this engine
            class_=AsyncSession,       # Use AsyncSession for async operations
            expire_on_commit=False     # Prevent automatic expiration of objects after commit
        )

    # ---------------------------- Async session generator ----------------------------
    # Provides a session dependency for FastAPI endpoints
    async def get_session(self):
        # Use async context manager to ensure session is properly closed
        async with self.async_session() as session:
            yield session  # Yield session to be injected into routes

# ---------------------------- Database Instance ----------------------------
# Create a single Database instance using settings
# This instance will be used throughout the application
database = Database(settings.DATABASE_URL)
