# ---------------------------- External Imports ----------------------------
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# ---------------------------- Settings Import ----------------------------
from app.core.settings import settings

# ---------------------------- Async Engine ----------------------------
class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(
            self.database_url,
            echo=True  # Logs SQL queries for debugging
        )
        self.async_session = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    # Async generator for DB session dependency
    async def get_session(self):
        async with self.async_session() as session:
            yield session

# ---------------------------- Database Instance ----------------------------
db = Database(settings.DATABASE_URL)
