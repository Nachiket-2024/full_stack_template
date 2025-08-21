# ---------------------------- External Imports ----------------------------
# Import select function from SQLAlchemy for building queries
from sqlalchemy.future import select

# Import AsyncSession for type hints and async database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Base CRUD Class Definition ----------------------------
# Generic async CRUD operations for any SQLAlchemy model
class BaseCRUD:

    # ---------------------------- Initialization ----------------------------
    # Initialize the CRUD instance with a SQLAlchemy model
    def __init__(self, model):
        # Store the SQLAlchemy ORM model class
        self.model = model

    # ---------------------------- Get Record by ID ----------------------------
    # Fetch a single record by its primary key ID
    async def get_by_id(self, db: AsyncSession, id: int):
        # Execute a select query filtered by the model's id
        result = await db.execute(select(self.model).where(self.model.id == id))
        # Return the single object or None if not found
        return result.scalar_one_or_none()

    # ---------------------------- Get All Records ----------------------------
    # Fetch all records of the model
    async def get_all(self, db: AsyncSession):
        # Execute a select query for all objects
        result = await db.execute(select(self.model))
        # Return a list of all objects
        return result.scalars().all()

    # ---------------------------- Get Record by Email ----------------------------
    # Fetch a record by the email field
    async def get_by_email(self, db: AsyncSession, email: str):
        # Execute a select query filtered by email
        result = await db.execute(select(self.model).where(self.model.email == email))
        # Return the single object or None if not found
        return result.scalar_one_or_none()

    # ---------------------------- Create New Record ----------------------------
    # Create a new record with provided data
    async def create(self, db: AsyncSession, obj_data: dict):
        # Instantiate the model with the provided dictionary data
        obj = self.model(**obj_data)
        # Add the object to the current DB session
        db.add(obj)
        # Commit the transaction to persist changes
        await db.commit()
        # Refresh the object to load any new DB-generated fields (like id)
        await db.refresh(obj)
        # Return the newly created object
        return obj

    # ---------------------------- Update Record ----------------------------
    # Update an existing record with provided data
    async def update(self, db: AsyncSession, db_obj, update_data: dict):
        # If no object is provided, return None
        if not db_obj:
            return None
        # Loop through the update dictionary and set attributes
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        # Add updated object to session
        db.add(db_obj)
        # Commit the transaction to save changes
        await db.commit()
        # Refresh the object to reflect latest DB state
        await db.refresh(db_obj)
        # Return the updated object
        return db_obj

    # ---------------------------- Update by Email ----------------------------
    # Fetch a record by email and update it with provided fields
    async def update_by_email(self, db: AsyncSession, email: str, update_data: dict):
        # Fetch object by email
        db_obj = await self.get_by_email(db, email)
        # Return None if object not found
        if not db_obj:
            return None
        # Update the object using the update method
        return await self.update(db, db_obj, update_data)

    # ---------------------------- Update Refresh Token ----------------------------
    # Update the refresh_token field of a record identified by email
    async def update_refresh_token(self, db: AsyncSession, email: str, refresh_token: str):
        # Use update_by_email to update only the refresh_token
        return await self.update_by_email(db, email, {"refresh_token": refresh_token})

    # ---------------------------- Delete Record ----------------------------
    # Delete a record from the database
    async def delete(self, db: AsyncSession, db_obj):
        # Return False if no object provided
        if not db_obj:
            return False
        # Delete the object from the session
        await db.delete(db_obj)
        # Commit the transaction
        await db.commit()
        # Return True to indicate successful deletion
        return True
