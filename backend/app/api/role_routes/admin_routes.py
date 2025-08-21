# ---------------------------- External Imports ----------------------------
# FastAPI router, Depends for DI, Header to read Authorization token
from fastapi import APIRouter, Depends, Header

# AsyncSession for async database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Pydantic schemas for Admin
from ...admin.admin_table.admin_schema import AdminCreate, AdminUpdate, AdminRead

# Database connection to provide async session
from ...database.connection import database

# Logic classes for admin CRUD operations
from ...admin.admin_logic.create_admin import create_admin
from ...admin.admin_logic.get_admin import get_admin
from ...admin.admin_logic.get_all_admin import get_all_admin
from ...admin.admin_logic.update_admin import update_admin
from ...admin.admin_logic.delete_admin import delete_admin

# ---------------------------- Admin API Router ----------------------------
# Create FastAPI router with prefix /admin and tag "Admin"
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# ---------------------------- Create Admin Endpoint ----------------------------
# POST /admin to create a new admin user (Admin only)
@router.post("/", response_model=AdminRead)
async def create_admin_endpoint(
    payload: AdminCreate,
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    # Extract JWT token from "Authorization: Bearer <token>"
    token = authorization.split(" ")[1]
    # Call modular logic class to create admin
    return await create_admin.execute(payload, db, token)

# ---------------------------- Get Admin by ID Endpoint ----------------------------
# GET /admin/{id} to fetch an admin user by ID (Admin only)
@router.get("/{id}", response_model=AdminRead)
async def get_admin_endpoint(
    id: int,
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    token = authorization.split(" ")[1]
    # Call modular logic class to fetch admin by ID
    return await get_admin.execute(id, db, token)

# ---------------------------- Get All Admin Users Endpoint ----------------------------
# GET /admin to fetch all admin users (Admin only)
@router.get("/", response_model=list[AdminRead])
async def get_all_admin_endpoint(
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    token = authorization.split(" ")[1]
    # Call modular logic class to fetch all admins
    return await get_all_admin.execute(db, token)

# ---------------------------- Update Admin Endpoint ----------------------------
# PUT /admin/{id} to update an admin user by ID (Admin only)
@router.put("/{id}", response_model=AdminRead)
async def update_admin_endpoint(
    id: int,
    payload: AdminUpdate,
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    token = authorization.split(" ")[1]
    # Call modular logic class to update admin
    return await update_admin.execute(id, payload, db, token)

# ---------------------------- Delete Admin Endpoint ----------------------------
# DELETE /admin/{id} to delete an admin user by ID (Admin only)
@router.delete("/{id}", response_model=dict)
async def delete_admin_endpoint(
    id: int,
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    token = authorization.split(" ")[1]
    # Call modular logic class to delete admin
    return await delete_admin.execute(id, db, token)
