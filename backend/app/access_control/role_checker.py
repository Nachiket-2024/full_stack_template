# ---------------------------- External Imports ----------------------------
# Import HTTPException, status codes, Header, and Depends for FastAPI dependencies
from fastapi import HTTPException, status, Header, Depends

# ---------------------------- Internal Imports ----------------------------
# Import the JWT service for token verification
from ..auth.token_logic.jwt_service import jwt_service

# ---------------------------- Role Checker Class ----------------------------
class RoleChecker:

    # ---------------------------- Initialization ----------------------------
    # No extra init needed; using jwt_service directly
    def __init__(self):
        pass

    # ---------------------------- Extract Token Dependency ----------------------------
    # Automatically extract token from Authorization header
    async def _get_token(self, authorization: str = Header(...)) -> str:
        # Ensure header starts with "Bearer "
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header must start with Bearer",
            )
        # Return only the raw token part after "Bearer "
        return authorization.split(" ")[1]

    # ---------------------------- Get Role from Token ----------------------------
    # Decode JWT token and extract the role
    async def get_role(self, token: str = Depends(_get_token)) -> str:
        # Decode token using jwt_service
        payload = await jwt_service.verify_token(token)

        # Raise 401 if token is invalid or expired
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        # Extract the role (table) from payload
        role = payload.get("table")
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not found in token",
            )
        return role

    # ---------------------------- Require Specific Role ----------------------------
    # Check if the user has the exact required role
    async def require_role(self, required_role: str, token: str = Depends(_get_token)) -> bool:
        role = await self.get_role(token)
        # Raise 403 if role does not match
        if role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role} privileges required",
            )
        return True

    # ---------------------------- Require Permission ----------------------------
    # Check if the user has a specific permission
    async def require_permission(self, permission: str, token: str = Depends(_get_token)) -> bool:
        role = await self.get_role(token)

        # Import here to avoid circular imports
        from ..access_control.role_permissions import role_permissions

        # Get allowed permissions for the role
        allowed_permissions = role_permissions.get(role, [])
        if permission not in allowed_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required for role '{role}'",
            )
        return True

    # ---------------------------- Get Full Payload ----------------------------
    # Decode token and return full payload including role and email
    async def get_payload(self, token: str = Depends(_get_token)) -> dict:
        payload = await jwt_service.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return payload

    # ---------------------------- Dependency Injector for Routes ----------------------------
    # Provides a FastAPI dependency for route functions
    def require_permission_dependency(self, permission: str):
        """
        FastAPI dependency that:
        1. Extracts token automatically
        2. Checks permission
        3. Returns role and email for route
        """
        async def wrapper(token: str = Depends(self._get_token)):
            # Check permission
            await self.require_permission(permission, token)
            # Return role and email from payload
            payload = await self.get_payload(token)
            return payload.get("table"), payload.get("email")
        return wrapper

# ---------------------------- Instantiate Role Checker ----------------------------
# Singleton instance for use in routes
role_checker = RoleChecker()
