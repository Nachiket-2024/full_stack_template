# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for Role1 table
from ..role1_table.role1_crud import role1_crud

# ---------------------------- GetAllRole1 Class ----------------------------
class GetAllRole1:
    def __init__(self):
        pass

    # Method to fetch all Role1 users
    async def execute(self, db: AsyncSession):

        # Fetch all users using CRUD
        objs = await role1_crud.get_all(db)
        
        # Return list of Role1 users
        return objs

# ---------------------------- Instance ----------------------------
get_all_role1 = GetAllRole1()
