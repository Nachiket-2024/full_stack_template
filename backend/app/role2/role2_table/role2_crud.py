# ---------------------------- Internal Imports ----------------------------
from ...database.base_crud import BaseCRUD
from .role2_model import Role2

# ---------------------------- Role2 CRUD Instance ----------------------------
# Instantiate BaseCRUD for Role2 table to handle async DB operations
role2_crud = BaseCRUD(Role2)
