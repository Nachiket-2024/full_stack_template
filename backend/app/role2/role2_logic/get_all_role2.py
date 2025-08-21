# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for Role2 table
from ..role2_table.role2_crud import role2_crud

# RoleChecker singleton to enforce admin-only access
from ...auth.utils.role_checker import role_checker

# ---------------------------- GetAllRole2 Class ----------------------------
class GetAllRole2:
    def __init__(self):
        pass

    async def execute(self, db: AsyncSession, token: str):
        # Admin-only access
        await role_checker.require_admin(token)

        # Fetch all Role2 users
        objs = await role2_crud.get_all(db)
        return objs

# ---------------------------- Instance ----------------------------
get_all_role2 = GetAllRole2()
