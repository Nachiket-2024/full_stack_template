# ---------------------------- Role Permissions Mapping ----------------------------
# Maps each role to the exact API actions they are allowed to access.
# The strings correspond to route/action names for easier readability.

# Role1: Basic user, limited to their own data
role1_permissions = [
    "get_my_profile",      # GET /users/me
    "update_my_profile",   # PUT /users/me
]

# Role2: Elevated user, can access own data + read all data
role2_permissions = [
    "get_my_profile",      # GET /users/me
    "update_my_profile",   # PUT /users/me
    "list_all_users",      # GET /users
]

# Admin: Full access to all routes
admin_permissions = [
    "get_my_profile",       # GET /users/me
    "update_my_profile",    # PUT /users/me
    "list_all_users",       # GET /users
    "update_any_user",      # PUT /users/{id}
    "delete_any_user",      # DELETE /users/{id}
    "manage_roles",         # POST/PUT/DELETE /roles
]

# ---------------------------- Central Mapping ----------------------------
# Dictionary mapping each role -> list of API route/action permissions
role_permissions = {
    "role1": role1_permissions,
    "role2": role2_permissions,
    "admin": admin_permissions,
}
