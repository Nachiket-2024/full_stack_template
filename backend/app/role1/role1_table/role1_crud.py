# ---------------------------- Internal Imports ----------------------------
from ...database.base_crud import BaseCRUD
from .role1_model import Role1

# ---------------------------- Role1 CRUD Instance ----------------------------
# Instantiate BaseCRUD for Role1 table to handle async DB operations
role1_crud = BaseCRUD(Role1)
