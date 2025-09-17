# ---------------------------- Internal Imports ----------------------------
# Import TokenBaseCRUD for generic token operations
from .token_crud_modules.token_base_crud import TokenBaseCRUD

# Import TokenEmailCRUD for email-specific token operations
from .token_crud_modules.token_email_crud import TokenEmailCRUD

# Import TokenAccessTokenCRUD for access-token-specific operations
from .token_crud_modules.token_access_token_crud import TokenAccessTokenCRUD

# Import TokenRefreshTokenCRUD for refresh-token-specific operations
from .token_crud_modules.token_refresh_token_crud import TokenRefreshTokenCRUD

# Import AsyncSession for type hints in method signatures
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- TokenCRUDCollector ----------------------------
# Facade class that bundles all 4 CRUD classes bound to a model
class TokenCRUDCollector:
    """
    Facade over all token-related CRUD classes. Provides direct access to
    methods of the underlying sub-CRUDs for convenience and IDE discovery.

    Sub-CRUDs and their forwarded methods:

    1. base (TokenBaseCRUD)
       1. get_by_id
       2. get_all
       3. create
       4. update
       5. delete

    2. email (TokenEmailCRUD)
       6. get_by_email
       7. update_by_email

    3. access (TokenAccessTokenCRUD)
       8. get_by_access_token
       9. update_by_access_token
       10. update_refresh_token_by_access_token

    4. refresh (TokenRefreshTokenCRUD)
       11. get_by_refresh_token
       12. update_by_refresh_token
       13. get_all_refresh_tokens
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self, model):
        """
        Input:
            1. model: SQLAlchemy model class for the token table.

        Process:
            1. Initialize each sub-CRUD class with the provided model.

        Output:
            1. None
        """
        # Instantiate TokenBaseCRUD with model
        self.base = TokenBaseCRUD(model)

        # Instantiate TokenEmailCRUD with model
        self.email = TokenEmailCRUD(model)

        # Instantiate TokenAccessTokenCRUD with model
        self.access = TokenAccessTokenCRUD(model)

        # Instantiate TokenRefreshTokenCRUD with model
        self.refresh = TokenRefreshTokenCRUD(model)

    # ---------------------------- Base Forwarders ----------------------------
    async def get_by_id(self, db: AsyncSession, id: int):
        return await self.base.get_by_id(db, id)

    async def get_all(self, db: AsyncSession):
        return await self.base.get_all(db)

    async def create(self, db: AsyncSession, obj_data: dict):
        return await self.base.create(db, obj_data)

    async def update(self, db: AsyncSession, db_obj, update_data: dict):
        return await self.base.update(db, db_obj, update_data)

    async def delete(self, db: AsyncSession, db_obj):
        return await self.base.delete(db, db_obj)

    # ---------------------------- Email Forwarders ----------------------------
    async def get_by_email(self, db: AsyncSession, email: str):
        return await self.email.get_by_email(db, email)

    async def update_by_email(self, db: AsyncSession, email: str, update_data: dict):
        return await self.email.update_by_email(db, email, update_data)

    # ---------------------------- Access Forwarders ----------------------------
    async def get_by_access_token(self, db: AsyncSession, access_token: str):
        return await self.access.get_by_access_token(db, access_token)

    async def update_by_access_token(self, db: AsyncSession, access_token: str, update_data: dict):
        return await self.access.update_by_access_token(db, access_token, update_data)

    async def update_refresh_token_by_access_token(
        self, db: AsyncSession, access_token: str, new_refresh_token: str
    ):
        return await self.access.update_refresh_token_by_access_token(db, access_token, new_refresh_token)

    # ---------------------------- Refresh Forwarders ----------------------------
    async def get_by_refresh_token(self, db: AsyncSession, refresh_token: str):
        return await self.refresh.get_by_refresh_token(db, refresh_token)

    async def update_by_refresh_token(self, db: AsyncSession, refresh_token: str, update_data: dict):
        return await self.refresh.update_by_refresh_token(db, refresh_token, update_data)

    async def get_all_refresh_tokens(self, db: AsyncSession, email: str):
        return await self.refresh.get_all_refresh_tokens(db, email)
    

# ---------------------------- Exports ----------------------------
__all__ = [
    "TokenBaseCRUD",
    "TokenEmailCRUD",
    "TokenAccessTokenCRUD",
    "TokenRefreshTokenCRUD",
    "TokenCRUDCollector",
]
