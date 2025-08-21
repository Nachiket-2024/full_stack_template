# ---------------------------- External Imports ----------------------------
# FastAPI router, Depends for DI, Header to read Authorization token
from fastapi import APIRouter, Depends, Header

# AsyncSession for async database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Pydantic schemas for Role2
from ...role2.role2_table.role2_schema import Role2Create, Role2Update, Role2Read

# Database connection to provide async session
from ...database.connection import database

# Logic classes for Role2 CRUD operations
from ...role2.role2_logic.create_role2 import create_role2
from ...role2.role2_logic.get_role2 import get_role2
from ...role2.role2_logic.get_all_role2 import get_all_role2
from ...role2.role2_logic.update_role2 import update_role2
from ...role2.role2_logic.delete_role2 import delete_role2

# ---------------------------- Role2 API Router ----------------------------
# Create FastAPI router with prefix /role2 and tag "Role2"
router = APIRouter(
    prefix="/role2",
    tags=["Role2"]
)

# ---------------------------- Create Role2 Endpoint ----------------------------
# POST /role2 to create a new Role2 user (Admin only)
@router.post("/", response_model=Role2Read)
async def create_role2_endpoint(
    payload: Role2Create,
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    # Extract JWT token from "Authorization: Bearer <token>"
    token = authorization.split(" ")[1]
    # Call modular logic class to create Role2
    return await create_role2.execute(payload, db, token)

# ---------------------------- Get Role2 by ID Endpoint ----------------------------
# GET /role2/{id} to fetch a Role2 user by ID (Admin only)
@router.get("/{id}", response_model=Role2Read)
async def get_role2_endpoint(
    id: int,
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    # Extract JWT token
    token = authorization.split(" ")[1]
    # Call modular logic class to fetch Role2 by ID
    return await get_role2.execute(id, db, token)

# ---------------------------- Get All Role2 Users Endpoint ----------------------------
# GET /role2 to fetch all Role2 users (Admin only)
@router.get("/", response_model=list[Role2Read])
async def get_all_role2_endpoint(
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    # Extract JWT token
    token = authorization.split(" ")[1]
    # Call modular logic class to fetch all Role2 users
    return await get_all_role2.execute(db, token)

# ---------------------------- Update Role2 Endpoint ----------------------------
# PUT /role2/{id} to update a Role2 user by ID (Admin only)
@router.put("/{id}", response_model=Role2Read)
async def update_role2_endpoint(
    id: int,
    payload: Role2Update,
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    # Extract JWT token
    token = authorization.split(" ")[1]
    # Call modular logic class to update Role2
    return await update_role2.execute(id, payload, db, token)

# ---------------------------- Delete Role2 Endpoint ----------------------------
# DELETE /role2/{id} to delete a Role2 user by ID (Admin only)
@router.delete("/{id}", response_model=dict)
async def delete_role2_endpoint(
    id: int,
    db: AsyncSession = Depends(database.get_session),
    authorization: str = Header(...)
):
    # Extract JWT token
    token = authorization.split(" ")[1]
    # Call modular logic class to delete Role2
    return await delete_role2.execute(id, db, token)
