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

# ---------------------------- UpdateRole2 Class ----------------------------
class UpdateRole2:
    def __init__(self):
        pass

    async def execute(self, id: int, payload, db: AsyncSession, token: str):
        # Admin-only access
        await role_checker.require_admin(token)

        # Fetch existing Role2 user
        db_obj = await role2_crud.get_by_id(db, id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Role2 not found")

        # Convert payload to dictionary for partial update
        update_data = payload.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = update_data.pop("password")

        # Update Role2 user
        updated_obj = await role2_crud.update(db, db_obj, update_data)
        return updated_obj

# ---------------------------- Instance ----------------------------
update_role2 = UpdateRole2()
