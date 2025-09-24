# ---------------------------- Internal Imports ----------------------------
# Import base CRUD operations for users
from .user_crud_modules.user_base_crud import UserBaseCRUD

# Import email-specific CRUD operations for users
from .user_crud_modules.user_email_crud import UserEmailCRUD

# Import AsyncSession for type hints in method signatures
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- UserCRUDCollector ----------------------------
# Facade class that bundles all user CRUD operations for convenience
class UserCRUDCollector:
    """
    Facade over user CRUD classes. Provides direct access to
    methods of the underlying sub-CRUDs for convenience and IDE discovery.

    Sub-CRUDs and their forwarded methods:

    1. base (UserBaseCRUD)
       1. get_by_id
       2. get_all
       3. create
       4. update
       5. delete

    2. email (UserEmailCRUD)
       6. get_by_email
       7. update_by_email
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self, model):
        """
        Input:
            1. model: SQLAlchemy model class for the user table.

        Process:
            1. Initialize each sub-CRUD class with the provided model.

        Output:
            1. None
        """
        # Step 1: Instantiate UserBaseCRUD with model.
        self.base = UserBaseCRUD(model)
        
        # Step 2: Instantiate UserEmailCRUD with model.
        self.email = UserEmailCRUD(model)

    # ---------------------------- Base Forwarders ----------------------------
    async def get_by_id(self, id: int, db: AsyncSession):
        return await self.base.get_by_id(id, db)

    async def get_all(self, db: AsyncSession):
        return await self.base.get_all(db)

    async def create(self, obj_data: dict, db: AsyncSession):
        return await self.base.create(obj_data, db)

    async def update(self, db_obj, update_data: dict, db: AsyncSession):
        return await self.base.update(db_obj, update_data, db)

    async def delete(self, db_obj, db: AsyncSession):
        return await self.base.delete(db_obj, db)

    # ---------------------------- Email Forwarders ----------------------------
    async def get_by_email(self, email: str, db: AsyncSession):
        return await self.email.get_by_email(email, db)

    async def update_by_email(self, email: str, update_data: dict, db: AsyncSession):
        return await self.email.update_by_email(email, update_data, db)


# ---------------------------- Exports ----------------------------
# Re-export all user CRUD classes and the collector to centralize imports
__all__ = [
    "UserBaseCRUD",
    "UserEmailCRUD",
    "UserCRUDCollector",
]
