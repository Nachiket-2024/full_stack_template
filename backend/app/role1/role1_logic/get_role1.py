# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI HTTPException
from fastapi import HTTPException

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for Role1 table
from ..role1_table.role1_crud import role1_crud

# ---------------------------- GetRole1 Class ----------------------------
class GetRole1:
    def __init__(self):
        pass

    # Method to fetch Role1 user by ID
    async def execute(self, id: int, db: AsyncSession):

        # Fetch user by ID using CRUD
        obj = await role1_crud.get_by_id(db, id)

        # Raise 404 if user not found
        if not obj:
            raise HTTPException(status_code=404, detail="Role1 not found")
        
        # Return Role1 object
        return obj

# ---------------------------- Instance ----------------------------
get_role1 = GetRole1()
