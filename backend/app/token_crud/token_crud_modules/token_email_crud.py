# ---------------------------- External Imports ----------------------------
# Import 'select' for constructing SQL queries asynchronously
from sqlalchemy.future import select

# Import 'AsyncSession' to handle asynchronous database sessions
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Token Email CRUD Class ----------------------------
class TokenEmailCRUD:
    """
    1. get_by_email - Fetch record by email.
    2. update_by_email - Update record identified by email.
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

    # ---------------------------- Get by Email ----------------------------
    async def get_by_email(self, db: AsyncSession, email: str):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. email (str): Email identifier.

        Process:
            1. Execute query filtering by email.

        Output:
            1. object | None: Record if found, else None.
        """
        # Execute query to find record by email
        result = await db.execute(select(self.model).where(self.model.email == email))

        # Return single object or None
        return result.scalar_one_or_none()

    # ---------------------------- Update by Email ----------------------------
    async def update_by_email(self, db: AsyncSession, email: str, update_data: dict):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. email (str): Email identifier.
            3. update_data (dict): Fields to update.

        Process:
            1. Fetch record by email.
            2. Update if found.

        Output:
            1. object | None: Updated record or None.
        """
        # Fetch record by email
        db_obj = await self.get_by_email(db, email)

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
