# ---------------------------- External Imports ----------------------------
# Import 'select' for constructing SQL queries asynchronously
from sqlalchemy.future import select

# Import 'AsyncSession' to handle asynchronous database sessions
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Token Refresh Token CRUD Class ----------------------------
class TokenRefreshTokenCRUD:
    """
    1. get_by_refresh_token - Fetch record by refresh token.
    2. update_by_refresh_token - Update record identified by refresh token.
    3. get_all_refresh_tokens - Fetch all refresh tokens for a given email.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self, model):
        """
        Input:
            1. model: SQLAlchemy model class.

        Process:
            1. Store model reference for CRUD operations.

        Output:
            1. None
        """
        # Store model reference for all queries
        self.model = model

    # ---------------------------- Get by Refresh Token ----------------------------
    async def get_by_refresh_token(self, db: AsyncSession, refresh_token: str):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. refresh_token (str): Refresh token value.

        Process:
            1. Execute query filtering by refresh_token.

        Output:
            1. object | None: Record if found, else None.
        """
        # Execute query to find record by refresh token
        result = await db.execute(select(self.model).where(self.model.refresh_token == refresh_token))

        # Return single object or None
        return result.scalar_one_or_none()

    # ---------------------------- Update by Refresh Token ----------------------------
    async def update_by_refresh_token(self, db: AsyncSession, refresh_token: str, update_data: dict):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. refresh_token (str): Token identifier.
            3. update_data (dict): Fields to update.

        Process:
            1. Fetch record by refresh_token.
            2. Update if found.

        Output:
            1. object | None: Updated record or None.
        """
        # Fetch record by refresh token
        db_obj = await self.get_by_refresh_token(db, refresh_token)

        # Return None if record not found
        if not db_obj:
            return None

        # Apply updates to record
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Add updated object to session
        db.add(db_obj)

        # Commit changes
        await db.commit()

        # Refresh object state
        await db.refresh(db_obj)

        # Return updated record
        return db_obj

    # ---------------------------- Get All Refresh Tokens for a User ----------------------------
    async def get_all_refresh_tokens(self, db: AsyncSession, email: str):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. email (str): Email address to filter tokens.

        Process:
            1. Execute query filtering all records by email.

        Output:
            1. list: List of refresh token ORM instances.
        """
        # Execute query to fetch all refresh tokens for given email
        result = await db.execute(select(self.model).where(self.model.email == email))

        # Return all matching objects as a list
        return result.scalars().all()
