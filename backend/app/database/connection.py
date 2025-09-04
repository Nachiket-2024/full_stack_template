# ---------------------------- External Imports ----------------------------
# Import SQLAlchemy async engine creator and AsyncSession type
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Import sessionmaker to create session factory for async sessions
from sqlalchemy.orm import sessionmaker

# ---------------------------- Settings Import ----------------------------
# Import application settings (contains DATABASE_URL, etc.)
from ..core.settings import settings

# ---------------------------- Database Class ----------------------------
# Encapsulates async engine creation and session management
class Database:
    """
    1. __init__ - Initialize database engine and session factory.
    2. get_session - Async generator to provide database session for endpoints.
    """

    # ---------------------------- Initialization ----------------------------
    def __init__(self, database_url: str):
        """
        Input:
            1. database_url (str): Connection URL for the database.

        Process:
            1. Store database URL.
            2. Create async SQLAlchemy engine.
            3. Configure session factory with AsyncSession.

        Output:
            1. None
        """
        # ---------------------------- Store Database URL ----------------------------
        self.database_url = database_url

        # ---------------------------- Create Async Engine ----------------------------
        self.engine = create_async_engine(
            self.database_url,
            echo=False  # Enable or disable SQL query logging for debugging
        )

        # ---------------------------- Create Session Factory ----------------------------
        self.async_session = sessionmaker(
            bind=self.engine,          # Bind sessions to this engine
            class_=AsyncSession,       # Use AsyncSession for async operations
            expire_on_commit=False     # Prevent automatic expiration of objects after commit
        )

    # ---------------------------- Async Session Generator ----------------------------
    async def get_session(self):
        """
        Input:
            1. None

        Process:
            1. Open async session using session factory.
            2. Yield session for FastAPI dependency injection.
            3. Ensure session is properly closed after use.

        Output:
            1. AsyncSession: Provides an active async database session.
        """
        # Use async context manager to ensure session closure
        async with self.async_session() as session:
            # Yield session to be injected into routes
            yield session


# ---------------------------- Database Instance ----------------------------
# Singleton database instance for use across the application
database = Database(settings.DATABASE_URL)
