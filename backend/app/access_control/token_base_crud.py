# ---------------------------- External Imports ----------------------------
# Import the 'select' function for building SQL queries in async context
from sqlalchemy.future import select

# Import the AsyncSession class for async DB session handling
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Token Base CRUD Class ----------------------------
# Define a generic CRUD class for managing token records in the database
class TokenBaseCRUD:
    """
    Generic async CRUD operations for token tables (access + refresh tokens).
    All token tables are expected to have:
        - id
        - email
        - access_token
        - refresh_token
        - created_at
        - updated_at
    Instantiate with a token model and use provided methods.
    """

    # ---------------------------- Initialization ----------------------------
    # Constructor to initialize the CRUD class with a specific SQLAlchemy model
    def __init__(self, model):
        """
        :param model: SQLAlchemy ORM token model
        """
        self.model = model

    # ---------------------------- Get by ID ----------------------------
    # Async method to fetch a token record by its primary key ID
    async def get_by_id(self, db: AsyncSession, id: int):
        """
        Fetch a token record by its primary key.
        """
        # Execute a SELECT query filtering by the given ID
        result = await db.execute(select(self.model).where(self.model.id == id))
        # Return one record or None if not found
        return result.scalar_one_or_none()

    # ---------------------------- Get all ----------------------------
    # Async method to fetch all token records
    async def get_all(self, db: AsyncSession):
        """
        Fetch all token records for this table.
        """
        # Execute a SELECT query to retrieve all rows
        result = await db.execute(select(self.model))
        # Return the list of objects
        return result.scalars().all()

    # ---------------------------- Get by Access Token ----------------------------
    # Async method to fetch a token by its access_token value
    async def get_by_access_token(self, db: AsyncSession, access_token: str):
        """
        Fetch a token record by its access token.
        """
        # Execute query filtering by access_token
        result = await db.execute(select(self.model).where(self.model.access_token == access_token))
        # Return one record or None
        return result.scalar_one_or_none()

    # ---------------------------- Get by Refresh Token ----------------------------
    # Async method to fetch a token by its refresh_token value
    async def get_by_refresh_token(self, db: AsyncSession, refresh_token: str):
        """
        Fetch a token record by its refresh token.
        """
        # Execute query filtering by refresh_token
        result = await db.execute(select(self.model).where(self.model.refresh_token == refresh_token))
        # Return one record or None
        return result.scalar_one_or_none()

    # ---------------------------- Get all Refresh Tokens for a User ----------------------------
    # Async method to fetch all refresh tokens linked to a specific user email
    async def get_all_refresh_tokens(self, email: str, db: AsyncSession) -> list[str]:
        """
        Fetch all refresh tokens for a given user (by email).
        Returns a list of refresh_token strings.
        """
        # Execute query to fetch only refresh_token column where email matches
        result = await db.execute(
            select(self.model.refresh_token).where(self.model.email == email)
        )
        # Return list of refresh_token values from the rows
        return [row[0] for row in result.fetchall()]

    # ---------------------------- Create a new token record ----------------------------
    # Async method to insert a new token record into the database
    async def create(self, db: AsyncSession, obj_data: dict):
        """
        Create a new token record.
        :param obj_data: Dictionary containing email, access_token, refresh_token, optional timestamps
        """
        # Create an instance of the model with given data
        obj = self.model(**obj_data)
        # Add object to the session
        db.add(obj)
        # Commit transaction
        await db.commit()
        # Refresh object to load DB-generated fields (like id, timestamps)
        await db.refresh(obj)
        # Return the created object
        return obj

    # ---------------------------- Update a record ----------------------------
    # Async method to update an existing record with given fields
    async def update(self, db: AsyncSession, db_obj, update_data: dict):
        """
        Update an existing token record with provided data.
        """
        # Loop through key-value pairs in update data
        for field, value in update_data.items():
            # Set attribute on the DB object
            setattr(db_obj, field, value)
        # Add updated object back to session
        db.add(db_obj)
        # Commit transaction
        await db.commit()
        # Refresh object to get updated state
        await db.refresh(db_obj)
        # Return the updated object
        return db_obj

    # ---------------------------- Update by Access Token ----------------------------
    # Async method to update a record found via access_token
    async def update_by_access_token(self, db: AsyncSession, access_token: str, update_data: dict):
        """
        Find a token record by access token and update it.
        """
        # Fetch the record by access_token
        db_obj = await self.get_by_access_token(db, access_token)
        # If not found, return None
        if not db_obj:
            return None
        # Otherwise update the record with provided data
        return await self.update(db, db_obj, update_data)

    # ---------------------------- Update Refresh Token by Access Token ----------------------------
    # Async method to update only refresh_token of a record found via access_token
    async def update_refresh_token_by_access_token(self, db: AsyncSession, access_token: str, new_refresh_token: str):
        """
        Update only the refresh_token for a record found via access_token.
        """
        # Call update_by_access_token with new refresh_token value
        return await self.update_by_access_token(db, access_token, {"refresh_token": new_refresh_token})

    # ---------------------------- Delete a record ----------------------------
    # Async method to delete a token record from the database
    async def delete(self, db: AsyncSession, db_obj):
        """
        Delete a token record from the database.
        """
        # Remove object from DB session
        await db.delete(db_obj)
        # Commit transaction
        await db.commit()
