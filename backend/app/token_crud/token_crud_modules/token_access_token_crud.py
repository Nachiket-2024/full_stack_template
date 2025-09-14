# ---------------------------- External Imports ----------------------------
# Import 'select' for constructing SQL queries asynchronously
from sqlalchemy.future import select

# Import 'AsyncSession' to handle asynchronous database sessions
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Token Access Token CRUD Class ----------------------------
class TokenAccessTokenCRUD:
    """
    1. get_by_access_token - Fetch record by access token.
    2. update_by_access_token - Update record identified by access token.
    3. update_refresh_token_by_access_token - Update refresh token using access token.
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

    # ---------------------------- Get by Access Token ----------------------------
    async def get_by_access_token(self, db: AsyncSession, access_token: str):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. access_token (str): Access token value.

        Process:
            1. Execute query filtering by access_token.

        Output:
            1. object | None: Record if found, else None.
        """
        # Execute query to find record by access token
        result = await db.execute(select(self.model).where(self.model.access_token == access_token))

        # Return single object or None
        return result.scalar_one_or_none()

    # ---------------------------- Update by Access Token ----------------------------
    async def update_by_access_token(self, db: AsyncSession, access_token: str, update_data: dict):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. access_token (str): Token identifier.
            3. update_data (dict): Fields to update.

        Process:
            1. Fetch record by access_token.
            2. Update if found.

        Output:
            1. object | None: Updated record or None.
        """
        # Fetch record by access token
        db_obj = await self.get_by_access_token(db, access_token)

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

    # ---------------------------- Update Refresh Token by Access Token ----------------------------
    async def update_refresh_token_by_access_token(self, db: AsyncSession, access_token: str, new_refresh_token: str):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. access_token (str): Access token identifier.
            3. new_refresh_token (str): New refresh token value.

        Process:
            1. Update refresh_token field using access_token.

        Output:
            1. object | None: Updated record or None.
        """
        # Use update_by_access_token helper to update refresh token
        return await self.update_by_access_token(db, access_token, {"refresh_token": new_refresh_token})
