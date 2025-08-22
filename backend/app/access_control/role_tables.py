# ---------------------------- Internal Imports ----------------------------
# Import BaseCRUD to create async CRUD operations for user tables
from .base_crud import BaseCRUD

# Import TokenBaseCRUD for specialized token operations
from .token_base_crud import TokenBaseCRUD

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
    "role1": BaseCRUD(Role1),
    "role2": BaseCRUD(Role2),
    "admin": BaseCRUD(Admin),
}

# ---------------------------- Centralized Token Tables ----------------------------
# Dictionary mapping role name -> TokenBaseCRUD instance for that role's token table
TOKEN_TABLES = {
    "role1": TokenBaseCRUD(Role1Token),
    "role2": TokenBaseCRUD(Role2Token),
    "admin": TokenBaseCRUD(AdminToken),
}

# ---------------------------- Default Role ----------------------------
# The fallback role to assign if none is explicitly specified
DEFAULT_ROLE = "role1"
