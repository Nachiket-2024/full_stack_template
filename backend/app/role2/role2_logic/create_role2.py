# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for Role2 table
from ..role2_table.role2_crud import role2_crud

# RoleChecker singleton to enforce admin-only access
from ...auth.utils.role_checker import role_checker

# ---------------------------- CreateRole2 Class ----------------------------
class CreateRole2:
    # Initialize class (no extra properties needed)
    def __init__(self):
        pass

    # Execute method to create a Role2 user
    async def execute(self, payload, db: AsyncSession, token: str):
        # Ensure only admin can create Role2
        await role_checker.require_admin(token)

        # Convert Pydantic payload to dictionary
        obj_data = payload.model_dump()

        # Hash password (replace with real hashing logic)
        obj_data["hashed_password"] = obj_data.pop("password")

        # Create Role2 user in database
        obj = await role2_crud.create(db, obj_data)
        return obj

# ---------------------------- Instance ----------------------------
create_role2 = CreateRole2()
