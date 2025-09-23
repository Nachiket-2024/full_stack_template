# ---------------------------- External Imports ----------------------------
# Import SQLAlchemy async engine creator and AsyncSession type
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Import sessionmaker to create a session factory for async sessions
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
    # Initialize database engine and session factory
    def __init__(self, database_url: str):
        """
        Input:
            1. database_url (str): Connection URL for the database.

        Process:
            1. Store database URL.
            2. Instantiate SQLAlchemy async engine for database connectivity.
            3. Configure session factory for producing AsyncSession objects.

        Output:
            1. None
        """
        # Step 1: Store Database URL
        self.database_url = database_url

        # Step 2: Instantiate SQLAlchemy async engine for database connectivity
        self.engine = create_async_engine(
            self.database_url,
            echo=False  # Enable SQL query logging for debugging if needed
        )

        # Step 3: Configure session factory for producing AsyncSession objects
        self.async_session = sessionmaker(
            bind=self.engine,          # Bind sessions to this engine
            class_=AsyncSession,       # Use AsyncSession for async operations
            expire_on_commit=False     # Prevent automatic expiration of objects after commit
        )

    # ---------------------------- Async Session Generator ----------------------------
    # Async generator to yield database sessions for dependency injection
    async def get_session(self):
        """
        Input:
            1. None

        Process:
            1. Use async context manager to ensure session closure.
            2. Yield session to be injected into routes.
            3. Session automatically closed after context exit.

        Output:
            1. AsyncSession: Provides an active async database session.
        """
        # Step 1: Use async context manager to ensure session closure
        async with self.async_session() as session:
            # Step 2: Yield session to be injected into routes
            yield session
            # Step 3: Session automatically closed after context exit


# ---------------------------- Database Instance ----------------------------
# Singleton database instance for use across the application
database = Database(settings.DATABASE_URL)
