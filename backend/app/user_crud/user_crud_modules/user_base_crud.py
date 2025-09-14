# ---------------------------- External Imports ----------------------------
# Import select function from SQLAlchemy for building queries
from sqlalchemy.future import select

# Import AsyncSession for type hints and async database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Base CRUD Operations ----------------------------
class UserBaseCRUD:
    """
    1. get_by_id - Fetch a single record by primary key ID.
    2. get_all - Fetch all records of the model.
    3. create - Create a new record with provided data.
    4. update - Update an existing record with provided data.
    5. delete - Delete a record from the database.
    """

    # ---------------------------- Initialization ----------------------------
    def __init__(self, model):
        # Store SQLAlchemy ORM model for CRUD operations
        self.model = model

    # ---------------------------- Get Record by ID ----------------------------
    async def get_by_id(self, db: AsyncSession, id: int):
        """
        Input:
            1. db (AsyncSession): Active database session.
            2. id (int): Primary key ID.

        Process:
            1. Execute a select query with model.id filter.
            2. Return matching record.

        Output:
            1. object | None: ORM instance or None if not found.
        """
        # Execute query by ID
        result = await db.execute(select(self.model).where(self.model.id == id))

        # Return single object or None
        return result.scalar_one_or_none()

    # ---------------------------- Get All Records ----------------------------
    async def get_all(self, db: AsyncSession):
        """
        Input:
            1. db (AsyncSession): Active database session.

        Process:
            1. Execute a select query for all model records.

        Output:
            1. list: List of ORM instances.
        """
        # Execute query for all records
        result = await db.execute(select(self.model))

        # Return all objects
        return result.scalars().all()

    # ---------------------------- Create New Record ----------------------------
    async def create(self, db: AsyncSession, obj_data: dict):
        """
        Input:
            1. db (AsyncSession): Active database session.
            2. obj_data (dict): Data for new record.

        Process:
            1. Instantiate ORM object.
            2. Add to session and commit.
            3. Refresh object with DB values.

        Output:
            1. object: Newly created ORM instance.
        """
        # Instantiate ORM object
        obj = self.model(**obj_data)

        # Add to session
        db.add(obj)

        # Commit transaction
        await db.commit()

        # Refresh object with DB values
        await db.refresh(obj)

        # Return new object
        return obj

    # ---------------------------- Update Record ----------------------------
    async def update(self, db: AsyncSession, db_obj, update_data: dict):
        """
        Input:
            1. db (AsyncSession): Active database session.
            2. db_obj (object): ORM object to update.
            3. update_data (dict): Fields and values to update.

        Process:
            1. Validate object exists.
            2. Update attributes.
            3. Commit and refresh object.

        Output:
            1. object | None: Updated object or None if not found.
        """
        # Return None if object missing
        if not db_obj:
            return None
        
        # Update fields dynamically
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Add updated object to session
        db.add(db_obj)

        # Commit transaction
        await db.commit()

        # Refresh object with DB values
        await db.refresh(db_obj)

        # Return updated object
        return db_obj

    # ---------------------------- Delete Record ----------------------------
    async def delete(self, db: AsyncSession, db_obj):
        """
        Input:
            1. db (AsyncSession): Active database session.
            2. db_obj (object): ORM object to delete.

        Process:
            1. Validate object exists.
            2. Delete and commit transaction.

        Output:
            1. bool: True if deleted, False if not found.
        """
        # Return False if no object
        if not db_obj:
            return False
        
        # Delete object
        await db.delete(db_obj)

        # Commit transaction
        await db.commit()

        # Return success
        return True
