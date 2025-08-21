# ---------------------------- External Imports ----------------------------
# SQLAlchemy async session and query tools
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Token Base CRUD Class ----------------------------
class TokenBaseCRUD:
    """
    Generic async CRUD operations for token tables (access + refresh tokens).
    All token tables are expected to have:
        - id
        - access_token
        - refresh_token
        - created_at
        - updated_at
    Instantiate with a token model and use provided methods.
    """

    # ---------------------------- Initialization ----------------------------
    def __init__(self, model):
        """
        :param model: SQLAlchemy ORM token model
        """
        self.model = model

    # ---------------------------- Get by ID ----------------------------
    async def get_by_id(self, db: AsyncSession, id: int):
        """
        Fetch a token record by its primary key.
        """
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    # ---------------------------- Get all ----------------------------
    async def get_all(self, db: AsyncSession):
        """
        Fetch all token records for this table.
        """
        result = await db.execute(select(self.model))
        return result.scalars().all()

    # ---------------------------- Get by Access Token ----------------------------
    async def get_by_access_token(self, db: AsyncSession, access_token: str):
        """
        Fetch a token record by its access token.
        """
        result = await db.execute(select(self.model).where(self.model.access_token == access_token))
        return result.scalar_one_or_none()

    # ---------------------------- Get by Refresh Token ----------------------------
    async def get_by_refresh_token(self, db: AsyncSession, refresh_token: str):
        """
        Fetch a token record by its refresh token.
        """
        result = await db.execute(select(self.model).where(self.model.refresh_token == refresh_token))
        return result.scalar_one_or_none()

    # ---------------------------- Create a new token record ----------------------------
    async def create(self, db: AsyncSession, obj_data: dict):
        """
        Create a new token record.
        :param obj_data: Dictionary containing access_token, refresh_token, optional timestamps
        """
        obj = self.model(**obj_data)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    # ---------------------------- Update a record ----------------------------
    async def update(self, db: AsyncSession, db_obj, update_data: dict):
        """
        Update an existing token record with provided data.
        """
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # ---------------------------- Update by Access Token ----------------------------
    async def update_by_access_token(self, db: AsyncSession, access_token: str, update_data: dict):
        """
        Find a token record by access token and update it.
        """
        db_obj = await self.get_by_access_token(db, access_token)
        if not db_obj:
            return None
        return await self.update(db, db_obj, update_data)

    # ---------------------------- Update Refresh Token by Access Token ----------------------------
    async def update_refresh_token_by_access_token(self, db: AsyncSession, access_token: str, new_refresh_token: str):
        """
        Update only the refresh_token for a record found via access_token.
        """
        return await self.update_by_access_token(db, access_token, {"refresh_token": new_refresh_token})

    # ---------------------------- Delete a record ----------------------------
    async def delete(self, db: AsyncSession, db_obj):
        """
        Delete a token record from the database.
        """
        await db.delete(db_obj)
        await db.commit()
