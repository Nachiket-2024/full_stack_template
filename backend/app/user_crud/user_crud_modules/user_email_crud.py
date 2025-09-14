# ---------------------------- External Imports ----------------------------
# Import select function from SQLAlchemy for building queries
from sqlalchemy.future import select

# Import AsyncSession for type hints and async database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Email CRUD Operations ----------------------------
class UserEmailCRUD:
    """
    1. get_by_email - Fetch a record by email field.
    2. update_by_email - Fetch a record by email and update it.
    """

    # ---------------------------- Initialization ----------------------------
    def __init__(self, model):
        # Store SQLAlchemy ORM model
        self.model = model

    # ---------------------------- Get Record by Email ----------------------------
    async def get_by_email(self, db: AsyncSession, email: str):
        """
        Input:
            1. db (AsyncSession): Active database session.
            2. email (str): Email to filter by.

        Process:
            1. Execute select query with email filter.

        Output:
            1. object | None: ORM instance or None if not found.
        """
        # Execute query by email
        result = await db.execute(select(self.model).where(self.model.email == email))

        # Return single object or None
        return result.scalar_one_or_none()

    # ---------------------------- Update Record by Email ----------------------------
    async def update_by_email(self, db: AsyncSession, email: str, update_data: dict):
        """
        Input:
            1. db (AsyncSession): Active database session.
            2. email (str): Email to filter by.
            3. update_data (dict): Fields and values to update.

        Process:
            1. Fetch record by email.
            2. Update record with given data.

        Output:
            1. object | None: Updated object or None if not found.
        """
        # Fetch object by email
        db_obj = await self.get_by_email(db, email)

        # Return None if not found
        if not db_obj:
            return None
        
        # Update object fields
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Add updated object to session
        db.add(db_obj)

        # Commit transaction
        await db.commit()

        # Refresh object
        await db.refresh(db_obj)

        # Return updated object
        return db_obj
