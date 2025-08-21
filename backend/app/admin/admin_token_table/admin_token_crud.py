# ---------------------------- Internal Imports ----------------------------

# Import generic token CRUD base
from ...database.token_base_crud import TokenBaseCRUD

# Import the AdminToken SQLAlchemy model
from .admin_token_model import AdminToken

# ---------------------------- AdminToken CRUD Instance ----------------------------

# Instantiate TokenBaseCRUD for AdminToken table
# Provides async methods: get_by_id, get_all, get_by_access_token, get_by_refresh_token,
# create, update, update_by_access_token, update_refresh_token_by_access_token, delete
admin_token_crud = TokenBaseCRUD(AdminToken)
