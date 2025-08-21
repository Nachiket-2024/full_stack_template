# ---------------------------- External Imports ----------------------------
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Base CRUD Class ----------------------------
class BaseCRUD:
    """
    Generic async CRUD operations for any SQLAlchemy model.
    Instantiate with a model and use the provided methods.
    """

    # ---------------------------- Initialization ----------------------------
    def __init__(self, model):
        """
        :param model: SQLAlchemy ORM model class
        """
        self.model = model

    # ---------------------------- Get by ID ----------------------------
    async def get_by_id(self, db: AsyncSession, id: int):
        """
        Fetch a single record by primary key.
        """
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    # ---------------------------- Get all ----------------------------
    async def get_all(self, db: AsyncSession):
        """
        Fetch all records for the model.
        """
        result = await db.execute(select(self.model))
        return result.scalars().all()

    # ---------------------------- Get by Email ----------------------------
    async def get_by_email(self, db: AsyncSession, email: str):
        """
        Fetch a single record by email field.
        """
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalar_one_or_none()

    # ---------------------------- Create a new record ----------------------------
    async def create(self, db: AsyncSession, obj_data: dict):
        """
        Create a new record.
        :param obj_data: Dictionary of fields to populate
        """
        obj = self.model(**obj_data)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    # ---------------------------- Update a record ----------------------------
    async def update(self, db: AsyncSession, db_obj, update_data: dict):
        """
        Update an existing record with provided data.
        """
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # ---------------------------- Update by Email ----------------------------
    async def update_by_email(self, db: AsyncSession, email: str, update_data: dict):
        """
        Fetch a record by email and update it with provided fields.
        Returns updated object or None if not found.
        """
        db_obj = await self.get_by_email(db, email)
        if not db_obj:
            return None
        return await self.update(db, db_obj, update_data)
    
    # ---------------------------- Update Refresh Token ----------------------------
    async def update_refresh_token(self, db: AsyncSession, email: str, refresh_token: str):
        """
        Fetch a record by email and update the refresh_token field.
        Returns updated object or None if not found.
        """
        return await self.update_by_email(db, email, {"refresh_token": refresh_token})

    # ---------------------------- Delete a record ----------------------------
    async def delete(self, db: AsyncSession, db_obj):
        """
        Delete a record from the database.
        """
        await db.delete(db_obj)
        await db.commit()
