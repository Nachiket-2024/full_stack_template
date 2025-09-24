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
    async def get_by_id(self, id: int, db: AsyncSession):
        """
        Input:
            1. id (int): Primary key ID.
            2. db (AsyncSession): Active database session.

        Process:
            1. Execute a select query with model.id filter.
            2. Return the matching record.

        Output:
            1. object | None: ORM instance or None if not found.
        """
        # Step 1: Execute a select query with model.id filter.
        result = await db.execute(select(self.model).where(self.model.id == id))
        
        # Step 2: Return the matching record.
        return result.scalar_one_or_none()

    # ---------------------------- Get All Records ----------------------------
    async def get_all(self, db: AsyncSession):
        """
        Input:
            1. db (AsyncSession): Active database session.

        Process:
            1. Execute a select query for all model records.
            2. Return all objects.

        Output:
            1. list: List of ORM instances.
        """
        # Step 1: Execute a select query for all model records.
        result = await db.execute(select(self.model))

        # Step 2: Return all objects.
        return result.scalars().all()

    # ---------------------------- Create New Record ----------------------------
    async def create(self, obj_data: dict, db: AsyncSession):
        """
        Input:
            1. obj_data (dict): Data for new record.
            2. db (AsyncSession): Active database session.

        Process:
            1. Instantiate ORM object with provided data.
            2. Add object to session.
            3. Commit transaction to persist changes.
            4. Refresh object to load DB-generated values.
            5. Return newly created object.

        Output:
            1. object: Newly created ORM instance.
        """
        # Step 1: Instantiate ORM object with provided data.
        obj = self.model(**obj_data)

        # Step 2: Add object to session.
        db.add(obj)

        # Step 3: Commit transaction to persist changes.
        await db.commit()

        # Step 4: Refresh object to load DB-generated values.
        await db.refresh(obj)

        # Step 5: Return newly created object.
        return obj

    # ---------------------------- Update Record ----------------------------
    async def update(self, db_obj, update_data: dict, db: AsyncSession):
        """
        Input:
            1. db_obj (object): ORM object to update.
            2. update_data (dict): Fields and values to update.
            3. db (AsyncSession): Active database session.

        Process:
            1. Return None if object does not exist.
            2. Update object attributes dynamically.
            3. Add updated object to session.
            4. Commit transaction.
            5. Refresh object with DB values.
            6. Return updated object.

        Output:
            1. object | None: Updated object or None if not found.
        """
        # Step 1: Return None if object does not exist.
        if not db_obj:
            return None
        
        # Step 2: Update object attributes dynamically.
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Step 3: Add updated object to session.
        db.add(db_obj)

        # Step 4: Commit transaction.
        await db.commit()

        # Step 5: Refresh object with DB values.
        await db.refresh(db_obj)

        # Step 6: Return updated object.
        return db_obj

    # ---------------------------- Delete Record ----------------------------
    async def delete(self, db_obj, db: AsyncSession):
        """
        Input:
            1. db_obj (object): ORM object to delete.
            2. db (AsyncSession): Active database session.

        Process:
            1. Return False if object does not exist.
            2. Delete object from session.
            3. Commit transaction.
            4. Return True if deletion succeeded.

        Output:
            1. bool: True if deleted, False if not found.
        """
        # Step 1: Return False if object does not exist.
        if not db_obj:
            return False
        
        # Step 2: Delete object from session.
        await db.delete(db_obj)

        # Step 3: Commit transaction.
        await db.commit()

        # Step 4: Return True if deletion succeeded.
        return True
