# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for admin table
from ..admin_table.admin_crud import admin_crud

# RoleChecker singleton for enforcing admin-only access
from ...auth.utils.role_checker import role_checker

# ---------------------------- DeleteAdmin Class ----------------------------
class DeleteAdmin:
    # Initialize class (no extra properties needed)
    def __init__(self):
        pass

    # Method to execute deleting an admin
    async def execute(self, id: int, db: AsyncSession, token: str):
        # Only admin can delete admin
        await role_checker.require_admin(token)

        # Fetch the admin by ID
        db_obj = await admin_crud.get_by_id(db, id)

        # Raise 404 if admin not found
        if not db_obj:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Admin not found")

        # Delete the admin using CRUD
        deleted = await admin_crud.delete(db, db_obj)

        # Return confirmation message
        return {"detail": "Admin deleted successfully" if deleted else "Admin not deleted"}

# ---------------------------- Instance ----------------------------
# Singleton instance for usage in router
delete_admin = DeleteAdmin()
