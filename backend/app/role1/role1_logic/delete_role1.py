# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI HTTPException
from fastapi import HTTPException

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for Role1 table
from ..role1_table.role1_crud import role1_crud

# RoleChecker singleton to enforce admin-only access
from ...auth.utils.role_checker import role_checker

# ---------------------------- DeleteRole1 Class ----------------------------
class DeleteRole1:
    def __init__(self):
        pass

    # Method to delete a Role1 user (Admin only)
    async def execute(self, id: int, db: AsyncSession, token: str):

        # Enforce admin-only access
        await role_checker.require_admin(token)

        # Fetch user by ID
        db_obj = await role1_crud.get_by_id(db, id)

        # Raise 404 if not found
        if not db_obj:
            raise HTTPException(status_code=404, detail="Role1 not found")
        
        # Delete user using CRUD
        deleted = await role1_crud.delete(db, db_obj)
        
        # Return confirmation message
        return {"detail": "Role1 deleted successfully" if deleted else "Role1 not deleted"}

# ---------------------------- Instance ----------------------------
delete_role1 = DeleteRole1()
