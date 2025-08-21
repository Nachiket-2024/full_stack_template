# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI HTTPException
from fastapi import HTTPException

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for Role1 table
from ..role1_table.role1_crud import role1_crud

# ---------------------------- UpdateRole1 Class ----------------------------
class UpdateRole1:
    def __init__(self):
        pass

    # Method to update a Role1 user
    async def execute(self, id: int, payload, db: AsyncSession):

        # Fetch existing user by ID
        db_obj = await role1_crud.get_by_id(db, id)

        # Raise 404 if not found
        if not db_obj:
            raise HTTPException(status_code=404, detail="Role1 not found")
        
        # Convert payload to dictionary for partial update
        update_data = payload.model_dump(exclude_unset=True)

        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = update_data.pop("password")

        # Update user using CRUD
        updated_obj = await role1_crud.update(db, db_obj, update_data)
        # Return updated Role1 object
        return updated_obj

# ---------------------------- Instance ----------------------------
update_role1 = UpdateRole1()
