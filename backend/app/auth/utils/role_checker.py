# ---------------------------- External Imports ----------------------------
# HTTP exception for unauthorized access
from fastapi import HTTPException, status

# ---------------------------- Internal Imports ----------------------------
# JWT service singleton to decode tokens
from ..token_logic.jwt_service import jwt_service

# ---------------------------- Role Checker Class ----------------------------
class RoleChecker:
    # ---------------------------- Initialization ----------------------------
    def __init__(self):
        # No extra init needed; using jwt_service directly
        pass

    # ---------------------------- Get Role from Token ----------------------------
    async def get_role(self, token: str):
        # Decode the JWT token using JWTService
        payload = await jwt_service.verify_token(token)
        # Raise 401 if token invalid
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        # Extract role/table from payload
        role = payload.get("table")
        # Raise 403 if table not present
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not found in token",
            )
        return role

    # ---------------------------- Require Admin ----------------------------
    async def require_admin(self, token: str):
        # Get role from token
        role = await self.get_role(token)
        # Only allow admin
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required",
            )
        return True

    # ---------------------------- Require Role2 ----------------------------
    async def require_role2(self, token: str):
        # Get role from token
        role = await self.get_role(token)
        # Only allow role2
        if role != "role2":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role2 privileges required",
            )
        return True

    # ---------------------------- Require Role1 ----------------------------
    async def require_role1(self, token: str):
        # Get role from token
        role = await self.get_role(token)
        # Only allow role1
        if role != "role1":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role1 privileges required",
            )
        return True


# ---------------------------- Instantiate Role Checker ----------------------------
role_checker = RoleChecker()
