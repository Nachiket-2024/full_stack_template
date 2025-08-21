# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for Role1 table
from ..role1_table.role1_crud import role1_crud

# ---------------------------- CreateRole1 Class ----------------------------
class CreateRole1:
    # Initialize class (no extra properties needed)
    def __init__(self):
        pass

    # Method to execute Role1 creation
    async def execute(self, payload, db: AsyncSession):
        # Convert Pydantic model to dictionary
        obj_data = payload.model_dump()

        # Hash password (replace with real hashing logic)
        obj_data["hashed_password"] = obj_data.pop("password")

        # Create Role1 user using CRUD
        obj = await role1_crud.create(db, obj_data)
        
        # Return created Role1 object
        return obj

# ---------------------------- Instance ----------------------------
# Singleton instance for usage in router
create_role1 = CreateRole1()
