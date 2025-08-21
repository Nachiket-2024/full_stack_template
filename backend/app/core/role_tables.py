# ---------------------------- Role Table CRUD Imports ----------------------------
from ..role1.role1_table.role1_crud import role1_crud
from ..role2.role2_table.role2_crud import role2_crud
from ..admin.admin_table.admin_crud import admin_crud

# ---------------------------- Token Table CRUD Imports ----------------------------
from ..admin.admin_token_table.admin_token_crud import admin_token_crud
from ..role1.role1_token_table.role1_token_crud import role1_token_crud
from ..role2.role2_token_table.role2_token_crud import role2_token_crud

# ---------------------------- Centralized Role Tables ----------------------------
ROLE_TABLES = {
    "role1": role1_crud,
    "role2": role2_crud,
    "admin": admin_crud,
}

# ---------------------------- Centralized Token Tables ----------------------------
TOKEN_TABLES = {
    "role1": role1_token_crud,
    "role2": role2_token_crud,
    "admin": admin_token_crud,
}

# ---------------------------- Default Role ----------------------------
DEFAULT_ROLE = "role1"
