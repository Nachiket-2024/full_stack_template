# ---------------------------- External Imports ----------------------------
# FastAPI router, request object, and JSON response handling
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, RedirectResponse

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
from ..auth_logic.account_verification_logic import handle_account_verification

# Utility to get client IP
from ..auth_services.client_ip_service import get_client_ip

# App settings (frontend & Google OAuth URLs, client ID/secret)
from ...core.settings import settings

# ---------------------------- Router ----------------------------
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------- Signup Endpoint ----------------------------
@router.post("/signup")
async def signup(payload: SignupSchema, ip_address: str = Depends(get_client_ip)):
    response, status = await handle_signup(payload.name, payload.email, payload.password, ip_address)
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Login Endpoint ----------------------------
@router.post("/login")
async def login(payload: LoginSchema, ip_address: str = Depends(get_client_ip)):
    response, status = await handle_login(payload.email, payload.password, ip_address)
    return JSONResponse(content=response, status_code=status)

# ---------------------------- OAuth2 Google Login Initiation ----------------------------
@router.get("/oauth2/login/google")
async def oauth2_login_google():
    """
    Redirects user to Google's OAuth2 consent screen.
    """
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    scopes = "openid email profile"
    redirect_uri = f"{settings.BACKEND_BASE_URL}/auth/oauth2/callback/google"
    auth_url = (
        f"{google_auth_url}?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scopes.replace(' ', '%20')}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(url=auth_url)

# ---------------------------- OAuth2 Google Callback ----------------------------
@router.get("/oauth2/callback/google")
async def oauth2_callback_google(code: str, ip_address: str = Depends(get_client_ip)):
    """
    Handles Google OAuth2 callback:
    1. Exchanges code for access token
    2. Retrieves user info
    3. Logs in or creates user
    4. Redirects frontend with JWT tokens
    """
    jwt_tokens, status = await handle_oauth2_login({"code": code}, ip_address)

    if status != 200:
        # Redirect frontend on error
        redirect_url = f"{settings.FRONTEND_BASE_URL}/oauth2-failure?error=login_failed"
    else:
        # Redirect frontend with JWT tokens
        redirect_url = (
            f"{settings.FRONTEND_BASE_URL}/oauth2-success"
            f"?access_token={jwt_tokens['access_token']}"
            f"&refresh_token={jwt_tokens['refresh_token']}"
        )
    return RedirectResponse(url=redirect_url)

# ---------------------------- Logout Endpoint ----------------------------
@router.post("/logout")
async def logout(payload: RefreshTokenSchema):
    response, status = await handle_logout(payload.refresh_token)
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Password Reset Request ----------------------------
@router.post("/password-reset/request")
async def password_reset_request(payload: PasswordResetRequestSchema, ip_address: str = Depends(get_client_ip)):
    response, status = await handle_password_reset_request(payload.email, ip_address)
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Password Reset Confirm ----------------------------
@router.post("/password-reset/confirm")
async def password_reset_confirm(payload: PasswordResetSchema, ip_address: str = Depends(get_client_ip)):
    response, status = await handle_password_reset_confirm(payload.token, payload.new_password, ip_address)
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Account Verification Endpoint ----------------------------
@router.get("/verify-account")
async def verify_account(token: str, table_name: str | None = None):
    """
    Endpoint to verify a user's account using the token sent via email.
    """
    response, status = await handle_account_verification(token, table_name)
    return JSONResponse(content=response, status_code=status)
