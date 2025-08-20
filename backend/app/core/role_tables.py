# ---------------------------- Role Table CRUD Imports ----------------------------
# Import CRUD objects for each role table
from ..role1.role1_crud import role1_crud
from ..role2.role2_crud import role2_crud
from ..admin.admin_crud import admin_crud

# ---------------------------- Centralized Role Tables ----------------------------
# Mapping of role names to CRUD objects for easy access
ROLE_TABLES = {
    "role1": role1_crud,
    "role2": role2_crud,
    "admin": admin_crud,
}

# ---------------------------- Default Role ----------------------------
# Default role assigned to new public users
DEFAULT_ROLE = "role1"
