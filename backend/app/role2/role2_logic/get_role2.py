# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for Role2 table
from ..role2_table.role2_crud import role2_crud

# RoleChecker singleton to enforce admin-only access
from ...auth.utils.role_checker import role_checker

# ---------------------------- GetRole2 Class ----------------------------
class GetRole2:
    def __init__(self):
        pass

    async def execute(self, id: int, db: AsyncSession, token: str):
        # Admin-only access
        await role_checker.require_admin(token)

        # Fetch Role2 user by ID
        obj = await role2_crud.get_by_id(db, id)
        if not obj:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Role2 not found")
        return obj

# ---------------------------- Instance ----------------------------
get_role2 = GetRole2()
