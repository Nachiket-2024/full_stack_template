# ---------------------------- Internal Imports ----------------------------

# Import generic token CRUD base
from ...database.token_base_crud import TokenBaseCRUD

# Import the Role2Token SQLAlchemy model
from .role2_token_model import Role2Token

# ---------------------------- Role2Token CRUD Instance ----------------------------

# Instantiate TokenBaseCRUD for Role2Token table
# Provides async methods: get_by_id, get_all, get_by_access_token, get_by_refresh_token,
# create, update, update_by_access_token, update_refresh_token_by_access_token, delete
role2_token_crud = TokenBaseCRUD(Role2Token)
