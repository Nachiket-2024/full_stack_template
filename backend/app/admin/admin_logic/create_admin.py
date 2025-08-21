# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for admin table
from ..admin_table.admin_crud import admin_crud

# RoleChecker singleton for enforcing admin-only access
from ...auth.utils.role_checker import role_checker

# ---------------------------- CreateAdmin Class ----------------------------
class CreateAdmin:
    # Initialize class (no extra properties needed)
    def __init__(self):
        pass

    # Method to execute admin creation
    async def execute(self, payload, db: AsyncSession, token: str):
        # Ensure only admin can create another admin
        await role_checker.require_admin(token)

        # Convert Pydantic payload to dictionary
        obj_data = payload.model_dump()

        # Hash the password before saving (replace with real logic)
        obj_data["hashed_password"] = obj_data.pop("password")

        # Create the admin using CRUD
        obj = await admin_crud.create(db, obj_data)

        # Return the created admin object
        return obj

# ---------------------------- Instance ----------------------------
# Singleton instance for usage in router
create_admin = CreateAdmin()
