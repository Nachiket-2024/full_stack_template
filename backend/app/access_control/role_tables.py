# ---------------------------- Internal Imports ----------------------------
# Import BaseCRUD to create async CRUD operations for user tables
from ..user_crud.user_crud_collector import UserCRUDCollector

# Import role models
from ..roles.role1.role1_model import Role1
from ..roles.role2.role2_model import Role2
from ..roles.admin.admin_model import Admin

# ---------------------------- Centralized Role Tables ----------------------------
# Dictionary mapping role name -> CRUD instance for that role's table
ROLE_TABLES = {
    "role1": UserCRUDCollector(Role1),
    "role2": UserCRUDCollector(Role2),
    "admin": UserCRUDCollector(Admin),
}

# ---------------------------- Default Role ----------------------------
# The fallback role to assign if none is explicitly specified
DEFAULT_ROLE = "role1"
