# ---------------------------- Internal Imports ----------------------------
# Import BaseCRUD to create async CRUD operations for user tables
from ..user_crud.user_crud_collector import UserCRUDCollector

# Import TokenBaseCRUD for specialized token operations
from ..token_crud.token_crud_collector import TokenCRUDCollector

# Import role models
from ..role1.role1_table.role1_model import Role1
from ..role2.role2_table.role2_model import Role2
from ..admin.admin_table.admin_model import Admin

# Import token models for each role
from ..admin.admin_token_table.admin_token_model import AdminToken
from ..role1.role1_token_table.role1_token_model import Role1Token
from ..role2.role2_token_table.role2_token_model import Role2Token

# ---------------------------- Centralized Role Tables ----------------------------
# Dictionary mapping role name -> CRUD instance for that role's table
ROLE_TABLES = {
    "role1": UserCRUDCollector(Role1),
    "role2": UserCRUDCollector(Role2),
    "admin": UserCRUDCollector(Admin),
}

# ---------------------------- Centralized Token Tables ----------------------------
# Dictionary mapping role name -> TokenBaseCRUD instance for that role's token table
TOKEN_TABLES = {
    "role1": TokenCRUDCollector(Role1Token),
    "role2": TokenCRUDCollector(Role2Token),
    "admin": TokenCRUDCollector(AdminToken),
}

# ---------------------------- Default Role ----------------------------
# The fallback role to assign if none is explicitly specified
DEFAULT_ROLE = "role1"
