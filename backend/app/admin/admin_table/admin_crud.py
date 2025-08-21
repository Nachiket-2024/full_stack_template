# ---------------------------- Internal Imports ----------------------------
from ...database.base_crud import BaseCRUD
from .admin_model import Admin

# ---------------------------- Admin CRUD Instance ----------------------------
# Instantiate BaseCRUD for Admin table to handle async DB operations
admin_crud = BaseCRUD(Admin)
