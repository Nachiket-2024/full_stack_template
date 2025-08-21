# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for Role2 table
from ..role2_table.role2_crud import role2_crud

# RoleChecker singleton to enforce admin-only access
from ...auth.utils.role_checker import role_checker

# HTTPException for handling errors
from fastapi import HTTPException

# ---------------------------- DeleteRole2 Class ----------------------------
class DeleteRole2:
    def __init__(self):
        pass

    async def execute(self, id: int, db: AsyncSession, token: str):
        # Admin-only access
        await role_checker.require_admin(token)

        # Fetch Role2 user by ID
        db_obj = await role2_crud.get_by_id(db, id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Role2 not found")

        # Delete user
        deleted = await role2_crud.delete(db, db_obj)
        return {"detail": "Role2 deleted successfully" if deleted else "Role2 not deleted"}

# ---------------------------- Instance ----------------------------
delete_role2 = DeleteRole2()
