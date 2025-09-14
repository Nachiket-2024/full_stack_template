# ---------------------------- External Imports ----------------------------
# Import 'select' for constructing SQL queries asynchronously
from sqlalchemy.future import select

# Import 'AsyncSession' to handle asynchronous database sessions
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Token Base CRUD Class ----------------------------
class TokenBaseCRUD:
    """
    1. get_by_id - Fetch record by primary key ID.
    2. get_all - Fetch all records of the model.
    3. create - Create a new record.
    4. update - Update an existing record.
    5. delete - Delete a record.
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

    # ---------------------------- Get by ID ----------------------------
    async def get_by_id(self, db: AsyncSession, id: int):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. id (int): Primary key.

        Process:
            1. Execute query filtering by id.

        Output:
            1. object | None: Record if found, else None.
        """
        # Execute SQL query to find record by id
        result = await db.execute(select(self.model).where(self.model.id == id))

        # Return single object or None
        return result.scalar_one_or_none()

    # ---------------------------- Get All Records ----------------------------
    async def get_all(self, db: AsyncSession):
        """
        Input:
            1. db (AsyncSession): Database session.

        Process:
            1. Execute query for all records.

        Output:
            1. list: All ORM instances.
        """
        # Execute query to select all records
        result = await db.execute(select(self.model))

        # Return list of all objects
        return result.scalars().all()

    # ---------------------------- Create Record ----------------------------
    async def create(self, db: AsyncSession, obj_data: dict):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. obj_data (dict): Data for new record.

        Process:
            1. Instantiate model.
            2. Add to session, commit, refresh.

        Output:
            1. object: Created record.
        """
        # Create model instance with data
        obj = self.model(**obj_data)

        # Add object to session
        db.add(obj)

        # Commit transaction to save changes
        await db.commit()

        # Refresh object to sync with database state
        await db.refresh(obj)

        # Return created object
        return obj

    # ---------------------------- Update Record ----------------------------
    async def update(self, db: AsyncSession, db_obj, update_data: dict):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. db_obj (object): Existing object.
            3. update_data (dict): Fields to update.

        Process:
            1. Apply updates.
            2. Commit and refresh.

        Output:
            1. object: Updated record.
        """
        # Apply each field update
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Add updated object to session
        db.add(db_obj)

        # Commit changes
        await db.commit()

        # Refresh object state
        await db.refresh(db_obj)

        # Return updated object
        return db_obj

    # ---------------------------- Delete Record ----------------------------
    async def delete(self, db: AsyncSession, db_obj):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. db_obj (object): Record to delete.

        Process:
            1. Delete record.
            2. Commit transaction.

        Output:
            1. None
        """
        # Delete object from session
        await db.delete(db_obj)

        # Commit transaction to apply deletion
        await db.commit()
