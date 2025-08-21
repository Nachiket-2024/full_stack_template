# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for admin table
from ..admin_table.admin_crud import admin_crud

# RoleChecker singleton for enforcing admin-only access
from ...auth.utils.role_checker import role_checker

# ---------------------------- GetAllAdmin Class ----------------------------
class GetAllAdmin:
    # Initialize class (no extra properties needed)
    def __init__(self):
        pass

    # Method to execute fetching all admins
    async def execute(self, db: AsyncSession, token: str):
        # Only admin can fetch all admins
        await role_checker.require_admin(token)

        # Fetch all admins using CRUD
        objs = await admin_crud.get_all(db)

        # Return the list of admins
        return objs

# ---------------------------- Instance ----------------------------
# Singleton instance for usage in router
get_all_admin = GetAllAdmin()
