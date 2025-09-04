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
    3. get_by_access_token - Fetch record by access token.
    4. get_by_refresh_token - Fetch record by refresh token.
    5. get_all_refresh_tokens - Fetch all refresh tokens for an email.
    6. create - Create a new record.
    7. update - Update an existing record.
    8. update_by_refresh_token - Update record identified by refresh token.
    9. update_by_access_token - Update record identified by access token.
    10. update_refresh_token_by_access_token - Update refresh token using access token.
    11. delete - Delete a record.
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
        # Store model for queries
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
        # Execute query by id
        result = await db.execute(select(self.model).where(self.model.id == id))
        # Return object or None
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
        # Execute query for all records
        result = await db.execute(select(self.model))
        # Return list of objects
        return result.scalars().all()

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
        # Execute query by access_token
        result = await db.execute(select(self.model).where(self.model.access_token == access_token))
        # Return object or None
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
        # Execute query by refresh_token
        result = await db.execute(select(self.model).where(self.model.refresh_token == refresh_token))
        # Return object or None
        return result.scalar_one_or_none()

    # ---------------------------- Get All Refresh Tokens for Email ----------------------------
    async def get_all_refresh_tokens(self, email: str, db: AsyncSession) -> list[str]:
        """
        Input:
            1. email (str): User email.
            2. db (AsyncSession): Database session.

        Process:
            1. Execute query filtering by email.
            2. Collect refresh tokens.

        Output:
            1. list[str]: List of refresh tokens.
        """
        # Execute query by email
        result = await db.execute(select(self.model.refresh_token).where(self.model.email == email))
        # Extract refresh tokens
        return [row[0] for row in result.fetchall()]

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
        # Create object
        obj = self.model(**obj_data)
        # Add to session
        db.add(obj)
        # Commit transaction
        await db.commit()
        # Refresh object with DB state
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
        # Update fields
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        # Add to session
        db.add(db_obj)
        # Commit transaction
        await db.commit()
        # Refresh object
        await db.refresh(db_obj)
        # Return updated object
        return db_obj

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
        # Fetch record
        db_obj = await self.get_by_refresh_token(db, refresh_token)
        # Return None if not found
        if not db_obj:
            return None
        # Update record
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
        # Fetch record
        db_obj = await self.get_by_access_token(db, access_token)
        # Return None if not found
        if not db_obj:
            return None
        # Update record
        return await self.update(db, db_obj, update_data)

    # ---------------------------- Update Refresh Token Using Access Token ----------------------------
    async def update_refresh_token_by_access_token(self, db: AsyncSession, access_token: str, new_refresh_token: str):
        """
        Input:
            1. db (AsyncSession): Database session.
            2. access_token (str): Token identifier.
            3. new_refresh_token (str): New refresh token.

        Process:
            1. Update refresh_token field.

        Output:
            1. object | None: Updated record or None.
        """
        # Update refresh_token via access_token
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
        # Delete object
        await db.delete(db_obj)
        # Commit transaction
        await db.commit()
