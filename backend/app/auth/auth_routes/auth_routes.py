# ---------------------------- External Imports ----------------------------
# FastAPI router and JSON response handling
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Schemas for request/response validation
from ..auth_schemas.login_schema import LoginSchema
from ..auth_schemas.signup_schema import SignupSchema
from ..auth_schemas.password_reset_schema import PasswordResetSchema
from ..auth_schemas.password_reset_request_schema import PasswordResetRequestSchema
from ..auth_schemas.refresh_token_schema import RefreshTokenSchema

# Modular logic functions
from ..auth_logic.signup_logic import handle_signup
from ..auth_logic.login_logic import handle_login
from ..auth_logic.oauth2_login_logic import handle_oauth2_login
from ..auth_logic.password_reset_logic import handle_password_reset_request, handle_password_reset_confirm
from ..auth_logic.logout_logic import handle_logout

# ---------------------------- Router ----------------------------
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------- Signup Endpoint ----------------------------
@router.post("/signup")
async def signup(payload: SignupSchema, request: Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    ip_address = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host
    response, status = await handle_signup(payload.name, payload.email, payload.password, ip_address)
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Login Endpoint ----------------------------
@router.post("/login")
async def login(payload: LoginSchema, request: Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    ip_address = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host
    response, status = await handle_login(payload.email, payload.password, ip_address)
    return JSONResponse(content=response, status_code=status)

# ---------------------------- OAuth2 Login Endpoint ----------------------------
@router.get("/oauth2/login")
async def oauth2_login(request: Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    ip_address = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host
    response, status = await handle_oauth2_login(request.query_params, ip_address)
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Logout Endpoint ----------------------------
@router.post("/logout")
async def logout(payload: RefreshTokenSchema):
    response, status = await handle_logout(payload.refresh_token)
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Password Reset Request ----------------------------
@router.post("/password-reset/request")
async def password_reset_request(payload: PasswordResetRequestSchema, request: Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    ip_address = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host
    response, status = await handle_password_reset_request(payload.email, ip_address)
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Password Reset Confirm ----------------------------
@router.post("/password-reset/confirm")
async def password_reset_confirm(payload: PasswordResetSchema, request: Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    ip_address = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host
    response, status = await handle_password_reset_confirm(payload.token, payload.new_password, ip_address)
    return JSONResponse(content=response, status_code=status)
