# ---------------------------- External Imports ----------------------------
# Import FastAPI router, dependency injection, and HTTP exceptions
from fastapi import APIRouter, Depends, HTTPException, status

# Import Async SQLAlchemy session for async database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Import singleton RoleChecker instance for permission checks
from ...access_control.role_checker import role_checker

# Import CRUD instances for all role-based user tables
from ...access_control.role_tables import ROLE_TABLES

# Import database connection abstraction to get async sessions
from ...database.connection import database

# ---------------------------- Router Setup ----------------------------
# Create a new API router for user-related endpoints
router = APIRouter(
    prefix="/users",  # Base path for all routes in this router
    tags=["Users"]    # Tag for API docs grouping
)

# ---------------------------- Get Own Profile ----------------------------
# Endpoint to fetch currently authenticated user's profile
@router.get("/me")
async def get_my_profile(
    data: tuple = Depends(role_checker.require_permission_dependency("get_my_profile")),
    db: AsyncSession = Depends(database.get_session)
):
    # Unpack role and email from dependency
    role, email = data

    # Select the correct CRUD table based on role
    user_crud = ROLE_TABLES[role]

    # Fetch the user's record from the database
    user = await user_crud.get_by_email(db=db, email=email)

    # Return user's role and profile information
    return {"role": role, "user": user}


# ---------------------------- Update Own Profile ----------------------------
# Endpoint allowing the user to update their own profile
@router.put("/me")
async def update_my_profile(
    update_data: dict,
    data: tuple = Depends(role_checker.require_permission_dependency("update_my_profile")),
    db: AsyncSession = Depends(database.get_session)
):
    # Unpack role and email
    role, email = data

    # Select the CRUD table for this role
    user_crud = ROLE_TABLES[role]

    # Fetch current user record
    user = await user_crud.get_by_email(db=db, email=email)

    # Apply updates to the user's record
    updated_user = await user_crud.update(db=db, db_obj=user, update_data=update_data)

    # Return the updated user object
    return updated_user


# ---------------------------- List All Users ----------------------------
# Endpoint to list all users (requires permission)
@router.get("/")
async def list_all_users(
    data: tuple = Depends(role_checker.require_permission_dependency("list_all_users")),
    db: AsyncSession = Depends(database.get_session)
):
    # Initialize a dictionary to hold users grouped by role
    all_users = {}

    # Iterate over all role tables to fetch all users
    for role, crud in ROLE_TABLES.items():
        users = await crud.get_all(db=db)
        all_users[role] = users

    # Return dictionary containing all users
    return all_users


# ---------------------------- Update Any User ----------------------------
# Admin-only endpoint to update any user's profile
@router.put("/{user_email}")
async def update_any_user(
    user_email: str,
    update_data: dict,
    data: tuple = Depends(role_checker.require_permission_dependency("update_any_user")),
    db: AsyncSession = Depends(database.get_session)
):
    # Search through all role tables to locate the user
    for role, crud in ROLE_TABLES.items():
        user = await crud.get_by_email(db=db, email=user_email)
        if user:
            # Update the found user's record
            updated_user = await crud.update(db=db, db_obj=user, update_data=update_data)
            return updated_user

    # Raise exception if user not found
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


# ---------------------------- Delete Any User ----------------------------
# Admin-only endpoint to delete any user's profile
@router.delete("/{user_email}")
async def delete_any_user(
    user_email: str,
    data: tuple = Depends(role_checker.require_permission_dependency("delete_any_user")),
    db: AsyncSession = Depends(database.get_session)
):
    # Search through all role tables to locate the user
    for role, crud in ROLE_TABLES.items():
        user = await crud.get_by_email(db=db, email=user_email)
        if user:
            # Delete the found user's record
            await crud.delete(db=db, db_obj=user)
            return {"detail": f"User {user_email} deleted"}

    # Raise exception if user not found
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


# ---------------------------- Manage Roles ----------------------------
# Admin-only endpoint to assign or revoke roles
@router.post("/manage-role")
async def manage_roles(
    user_email: str,
    new_role: str,
    data: tuple = Depends(role_checker.require_permission_dependency("manage_roles")),
    db: AsyncSession = Depends(database.get_session)
):
    # Admin role already enforced by dependency
    role, _ = data

    # Validate the new role exists
    if new_role not in ROLE_TABLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    # Remove user from old role table
    for r, crud in ROLE_TABLES.items():
        user = await crud.get_by_email(db=db, email=user_email)
        if user:
            await crud.delete(db=db, db_obj=user)
            break

    # Add user to the new role table
    new_crud = ROLE_TABLES[new_role]
    await new_crud.create(db=db, obj_data={"email": user_email})

    # Return success message
    return {"detail": f"User {user_email} moved to role {new_role}"}
