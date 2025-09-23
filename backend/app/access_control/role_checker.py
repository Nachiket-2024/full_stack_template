# ---------------------------- External Imports ----------------------------
# Import FastAPI dependencies for HTTP exceptions, status codes, header extraction, and dependency injection
from fastapi import HTTPException, status, Header, Depends

# ---------------------------- Internal Imports ----------------------------
# Import JWT service to decode and verify tokens
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
        # No initialization logic required
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
        # Step 1: Validate header starts with 'Bearer '
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header must start with Bearer",
            )

        # Step 2: Extract token string after 'Bearer '
        return authorization.split(" ")[1]

    # ---------------------------- Get Role from Token ----------------------------
    async def get_role(self, token: str = Depends(_get_token)) -> str:
        """
        Input:
            1. token (str): JWT token.

        Process:
            1. Decode token using jwt_service.
            2. Validate token and raise error if invalid or expired.
            3. Extract role from payload and raise error if missing.

        Output:
            1. str: Role (table) from JWT payload.
        """
        # Step 1: Decode token using jwt_service
        payload = await jwt_service.verify_token(token)

        # Step 2: Validate token and raise error if invalid or expired
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        # Step 3: Extract role from payload and raise error if missing
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
            1. Get role from token.
            2. Compare role with required_role and raise error if mismatch.

        Output:
            1. bool: True if role matches, else raises HTTPException.
        """
        # Step 1: Get role from token
        role = await self.get_role(token)

        # Step 2: Compare role with required_role and raise error if mismatch
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
            1. Get role from token.
            2. Retrieve allowed permissions for role.
            3. Validate permission and raise error if not allowed.

        Output:
            1. bool: True if permission allowed, else raises HTTPException.
        """
        # Step 1: Get role from token
        role = await self.get_role(token)

        # Step 2: Retrieve allowed permissions for role
        from ..access_control.role_permissions import role_permissions
        allowed_permissions = role_permissions.get(role, [])

        # Step 3: Validate permission and raise error if not allowed
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
            2. Validate token and raise error if invalid or expired.

        Output:
            1. dict: Decoded JWT payload.
        """
        # Step 1: Decode token using jwt_service
        payload = await jwt_service.verify_token(token)

        # Step 2: Validate token and raise error if invalid or expired
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        return payload

    # ---------------------------- Dependency Injector for Routes ----------------------------
    def require_permission_dependency(self, permission: str):
        """
        Input:
            1. permission (str): The permission required to access the route.

        Process:
            1. Define a dependency wrapper function to be used by FastAPI.
            2. Validate the permission against the token.
            3. Retrieve the JWT payload associated with the token.
            4. Return role/table and email from the payload inside the wrapper.
            5. Return the wrapper function to be used as a dependency in routes.

        Output:
            1. async function: FastAPI dependency returning 'table' and 'email' from the payload.
        """
        # Step 1: Define a dependency wrapper function to be used by FastAPI
        async def wrapper(token: str = Depends(self._get_token)):
            # Step 2: Validate the permission against the token
            await self.require_permission(permission, token)

            # Step 3: Retrieve the JWT payload associated with the token
            payload = await self.get_payload(token)

            # Step 4: Return role/table and email from the payload inside the wrapper
            return payload.get("table"), payload.get("email")

        # Step 5: Return the wrapper to be used as a dependency in routes
        return wrapper


# ---------------------------- Instantiate Role Checker ----------------------------
# Singleton instance for use in routes
role_checker = RoleChecker()
