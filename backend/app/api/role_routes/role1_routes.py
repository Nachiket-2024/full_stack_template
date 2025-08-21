# ---------------------------- External Imports ----------------------------
# FastAPI router, Depends for DI, Header to read Authorization token
from fastapi import APIRouter, Depends, Header

# AsyncSession for async database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Pydantic schemas for Role1
from ...role1.role1_table.role1_schema import Role1Create, Role1Update, Role1Read

# Database connection to provide async session
from ...database.connection import database

# Logic classes for Role1 CRUD operations
from ...role1.role1_logic.create_role1 import create_role1
from ...role1.role1_logic.get_role1 import get_role1
from ...role1.role1_logic.get_all_role1 import get_all_role1
from ...role1.role1_logic.update_role1 import update_role1
from ...role1.role1_logic.delete_role1 import delete_role1

# ---------------------------- Role1 API Router ----------------------------
# Create FastAPI router with prefix /role1 and tag "Role1"
router = APIRouter(
    prefix="/role1",
    tags=["Role1"]
)

# ---------------------------- Create Role1 Endpoint ----------------------------
# POST /role1 to create a new Role1 user
@router.post("/", response_model=Role1Read)
async def create_role1_endpoint(
    payload: Role1Create,
    db: AsyncSession = Depends(database.get_session)
):
    # Call modular logic class to create Role1
    return await create_role1.execute(payload, db)

# ---------------------------- Get Role1 by ID Endpoint ----------------------------
# GET /role1/{id} to fetch a Role1 user by ID
@router.get("/{id}", response_model=Role1Read)
async def get_role1_endpoint(
    id: int,
    db: AsyncSession = Depends(database.get_session)
):
    # Call modular logic class to fetch Role1 by ID
    return await get_role1.execute(id, db)

# ---------------------------- Get All Role1 Users Endpoint ----------------------------
# GET /role1 to fetch all Role1 users
@router.get("/", response_model=list[Role1Read])
async def get_all_role1_endpoint(
    db: AsyncSession = Depends(database.get_session)
):
    # Call modular logic class to fetch all Role1 users
    return await get_all_role1.execute(db)

# ---------------------------- Update Role1 Endpoint ----------------------------
# PUT /role1/{id} to update a Role1 user by ID
@router.put("/{id}", response_model=Role1Read)
async def update_role1_endpoint(
    id: int,
    payload: Role1Update,
    db: AsyncSession = Depends(database.get_session)
):
    # Call modular logic class to update Role1
    return await update_role1.execute(id, payload, db)

# ---------------------------- Delete Role1 Endpoint ----------------------------
# DELETE /role1/{id} to delete a Role1 user by ID (Admin only)
@router.delete("/{id}", response_model=dict)
async def delete_role1_endpoint(
    id: int,
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    # Extract JWT token from "Authorization: Bearer <token>"
    token = authorization.split(" ")[1]
    # Call modular logic class to delete Role1 (admin enforcement inside logic)
    return await delete_role1.execute(id, db, token)
