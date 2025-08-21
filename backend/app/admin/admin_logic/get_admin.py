# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for admin table
from ..admin_table.admin_crud import admin_crud

# RoleChecker singleton for enforcing admin-only access
from ...auth.utils.role_checker import role_checker

# ---------------------------- GetAdmin Class ----------------------------
class GetAdmin:
    # Initialize class (no extra properties needed)
    def __init__(self):
        pass

    # Method to execute fetching an admin by ID
    async def execute(self, id: int, db: AsyncSession, token: str):
        # Only admin can fetch admin info
        await role_checker.require_admin(token)

        # Fetch the admin using CRUD
        obj = await admin_crud.get_by_id(db, id)

        # Raise 404 if not found
        if not obj:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Admin not found")

        # Return the fetched admin object
        return obj

# ---------------------------- Instance ----------------------------
# Singleton instance for usage in router
get_admin = GetAdmin()
