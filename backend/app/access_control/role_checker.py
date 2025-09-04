# ---------------------------- External Imports ----------------------------
# Import HTTPException, status codes, Header, and Depends for FastAPI dependencies
from fastapi import HTTPException, status, Header, Depends

# ---------------------------- Internal Imports ----------------------------
# Import the JWT service for token verification
from ..auth.token_logic.jwt_service import jwt_service

# ---------------------------- Role Checker Class ----------------------------
class RoleChecker:
    """
    1. _get_token - Extract raw token from Authorization header.
    2. get_role - Decode JWT and return user's role.
    3. require_role - Ensure user has specific role.
    4. require_permission - Ensure user has specific permission.
    5. get_payload - Return full decoded JWT payload.
    6. require_permission_dependency - FastAPI dependency returning role and email.
    """

    # ---------------------------- Initialization ----------------------------
    def __init__(self):
        # No initialization logic needed
        pass

    # ---------------------------- Extract Token Dependency ----------------------------
    async def _get_token(self, authorization: str = Header(...)) -> str:
        """
        Input:
            1. authorization (str): Full Authorization header.

        Process:
            1. Validate header starts with 'Bearer '.
            2. Extract token string after 'Bearer '.

        Output:
            1. str: Raw JWT token.
        """
        # Validate that the header starts with Bearer
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header must start with Bearer",
            )
        # Extract and return only the raw token
        return authorization.split(" ")[1]

    # ---------------------------- Get Role from Token ----------------------------
    async def get_role(self, token: str = Depends(_get_token)) -> str:
        """
        Input:
            1. token (str): JWT token.

        Process:
            1. Decode token using jwt_service.
            2. Validate token and extract role.

        Output:
            1. str: Role (table) from JWT payload.
        """
        # Decode the token using jwt_service
        payload = await jwt_service.verify_token(token)

        # Raise error if token is invalid or expired
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        # Extract role (table) from payload
        role = payload.get("table")
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not found in token",
            )
        return role

    # ---------------------------- Require Specific Role ----------------------------
    async def require_role(self, required_role: str, token: str = Depends(_get_token)) -> bool:
        """
        Input:
            1. required_role (str): Role to check.
            2. token (str): JWT token.

        Process:
            1. Decode token and get role.
            2. Compare with required_role.

        Output:
            1. bool: True if role matches, else raises HTTPException.
        """
        # Get the role from token
        role = await self.get_role(token)

        # Compare with required_role
        if role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role} privileges required",
            )
        return True

    # ---------------------------- Require Permission ----------------------------
    async def require_permission(self, permission: str, token: str = Depends(_get_token)) -> bool:
        """
        Input:
            1. permission (str): Permission to check.
            2. token (str): JWT token.

        Process:
            1. Decode token and get role.
            2. Retrieve allowed permissions for role.
            3. Validate permission.

        Output:
            1. bool: True if permission allowed, else raises HTTPException.
        """
        # Extract role from token
        role = await self.get_role(token)

        # Import role_permissions here to avoid circular imports
        from ..access_control.role_permissions import role_permissions

        # Get permissions allowed for the role
        allowed_permissions = role_permissions.get(role, [])

        # Validate the requested permission
        if permission not in allowed_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required for role '{role}'",
            )
        return True

    # ---------------------------- Get Full Payload ----------------------------
    async def get_payload(self, token: str = Depends(_get_token)) -> dict:
        """
        Input:
            1. token (str): JWT token.

        Process:
            1. Decode token using jwt_service.
            2. Validate token.

        Output:
            1. dict: Decoded JWT payload.
        """
        # Decode the token
        payload = await jwt_service.verify_token(token)

        # Validate token
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return payload

    # ---------------------------- Dependency Injector for Routes ----------------------------
    def require_permission_dependency(self, permission: str):
        """
        FastAPI dependency that:
            1. Extracts token automatically.
            2. Checks permission.
            3. Returns role and email for route.
        """
        # Define dependency wrapper
        async def wrapper(token: str = Depends(self._get_token)):
            # Ensure permission is valid
            await self.require_permission(permission, token)
            # Extract payload
            payload = await self.get_payload(token)
            # Return role and email
            return payload.get("table"), payload.get("email")

        # Return dependency wrapper
        return wrapper


# ---------------------------- Instantiate Role Checker ----------------------------
# Singleton instance for use in routes
role_checker = RoleChecker()
