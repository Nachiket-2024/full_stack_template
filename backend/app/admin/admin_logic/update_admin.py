# ---------------------------- External Imports ----------------------------
# Async database session type hint
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# CRUD instance for admin table
from ..admin_table.admin_crud import admin_crud

# RoleChecker singleton for enforcing admin-only access
from ...auth.utils.role_checker import role_checker

# ---------------------------- UpdateAdmin Class ----------------------------
class UpdateAdmin:
    # Initialize class (no extra properties needed)
    def __init__(self):
        pass

    # Method to execute updating an admin
    async def execute(self, id: int, payload, db: AsyncSession, token: str):
        # Only admin can update admin
        await role_checker.require_admin(token)

        # Fetch existing admin using CRUD
        db_obj = await admin_crud.get_by_id(db, id)

        # Raise 404 if admin not found
        if not db_obj:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Admin not found")

        # Convert payload to dictionary (partial update)
        update_data = payload.model_dump(exclude_unset=True)

        # Hash password if present
        if "password" in update_data:
            update_data["hashed_password"] = update_data.pop("password")

        # Update the admin using CRUD
        updated_obj = await admin_crud.update(db, db_obj, update_data)

        # Return the updated admin object
        return updated_obj

# ---------------------------- Instance ----------------------------
# Singleton instance for usage in router
update_admin = UpdateAdmin()
