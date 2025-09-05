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
    3. get_by_email - Fetch record by email.
    4. get_by_access_token - Fetch record by access token.
    5. get_by_refresh_token - Fetch record by refresh token.
    6. create - Create a new record.
    7. update - Update an existing record.
    8. update_by_email - Update record identified by email.
    9. update_by_access_token - Update record identified by access token.
    10. update_by_refresh_token - Update record identified by refresh token.
    11. update_refresh_token_by_access_token - Update refresh token using access token.
    12. delete - Delete a record.
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
        # Update record with new data
        return await self.update(db, db_obj, update_data)

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
        # Update record with new data
        return await self.update(db, db_obj, update_data)

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
        # Update record with new data
        return await self.update(db, db_obj, update_data)

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
