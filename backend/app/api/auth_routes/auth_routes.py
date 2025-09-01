# ---------------------------- External Imports ----------------------------
# FastAPI router for grouping endpoints, Depends for dependency injection, and response handling
from fastapi import APIRouter, Depends

# Async SQLAlchemy session for database interactions
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI Cookie dependency to read cookies from requests
from fastapi import Cookie

# ---------------------------- Internal Imports ----------------------------
# Schema for signup requests
from ...auth.signup.signup_schema import SignupSchema

# Schema for login requests
from ...auth.login.login_schema import LoginSchema

# Schema for password reset confirmation requests
from ...auth.password_reset_confirm.password_reset__confirm_schema import PasswordResetConfirmSchema

# Schema for password reset request
from ...auth.password_reset_request.password_reset_request_schema import PasswordResetRequestSchema

# Schema for refresh token handling
from ...auth.token_logic.refresh_token_schema import RefreshTokenSchema

# Handler to process user registration
from ...auth.signup.signup_handler import signup_handler

# Handler to process user login
from ...auth.login.login_handler import login_handler

# Handler to initiate OAuth2 login (e.g., Google)
from ...auth.oauth2.oauth2_login_handler import oauth2_login_handler

# Handler to retrieve current authenticated user info
from ...auth.current_user.current_user_handler import current_user_handler

# Handler for password reset request
from ...auth.password_reset_request.password_reset_request_handler import password_reset_request_handler

# Handler for password reset confirmation
from ...auth.password_reset_confirm.password_reset_confirm_handler import password_reset_confirm_handler

# Handler for logging out a single session
from ...auth.logout.logout_handler import logout_handler

# Handler for logging out from all devices
from ...auth.logout.logout_all_handler import logout_all_handler

# Handler for account verification
from ...auth.verify_account.account_verification_handler import account_verification_handler

# Service for rate limiting endpoints to prevent abuse
from ...auth.security.rate_limiter_service import rate_limiter_service

# Database connection for obtaining async sessions
from ...database.connection import database

# ---------------------------- Router ----------------------------
# FastAPI router instance with "/auth" prefix and Authentication tag
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------- Signup Endpoint ----------------------------
# POST /signup endpoint with rate limiting applied
@router.post("/signup")
@rate_limiter_service.rate_limited("signup")
async def signup(payload: SignupSchema, db: AsyncSession = Depends(database.get_session)):
    # Call signup handler with provided user details
    return await signup_handler.handle_signup(payload.name, payload.email, payload.password, db=db)

# ---------------------------- Login Endpoint ----------------------------
# POST /login endpoint with rate limiting applied
@router.post("/login")
@rate_limiter_service.rate_limited("login")
async def login(payload: LoginSchema, db: AsyncSession = Depends(database.get_session)):
    # Call login handler with provided credentials
    return await login_handler.handle_login(payload.email, payload.password, db=db)

# ---------------------------- OAuth2 Login Endpoints ----------------------------
# Initiate OAuth2 login with Google
@router.get("/oauth2/login/google")
@rate_limiter_service.rate_limited("oauth2_login")
async def oauth2_login_google():
    return await oauth2_login_handler.handle_oauth2_login_initiate()

# Callback endpoint for Google OAuth2 login
@router.get("/oauth2/callback/google")
@rate_limiter_service.rate_limited("oauth2_callback")
async def oauth2_callback_google(code: str, db=Depends(database.get_session)):
    return await oauth2_login_handler.handle_oauth2_callback(code, db=db)

# ---------------------------- Current User Endpoint ----------------------------
# GET /me to fetch current logged-in user info from access token cookie
@router.get("/me")
async def get_current_user(access_token: str = Cookie(None), db: AsyncSession = Depends(database.get_session)):
    return await current_user_handler.get_current_user(access_token, db)

# ---------------------------- Logout Endpoint ----------------------------
# POST /logout endpoint with rate limiting
@router.post("/logout")
@rate_limiter_service.rate_limited("logout")
async def logout(payload: RefreshTokenSchema, db: AsyncSession = Depends(database.get_session)):
    # Logout single session using refresh token
    return await logout_handler.handle_logout(payload.refresh_token)

# ---------------------------- Logout All Devices Endpoint ----------------------------
# POST /logout/all endpoint with rate limiting
@router.post("/logout/all")
@rate_limiter_service.rate_limited("logout_all")
async def logout_all(payload: RefreshTokenSchema, db: AsyncSession = Depends(database.get_session)):
    # Logout user from all devices using refresh token
    return await logout_all_handler.handle_logout_all(payload.refresh_token, db=db)

# ---------------------------- Password Reset Request ----------------------------
# POST /password-reset/request endpoint with rate limiting
@router.post("/password-reset/request")
@rate_limiter_service.rate_limited("password_reset_request")
async def password_reset_request(payload: PasswordResetRequestSchema, db: AsyncSession = Depends(database.get_session)):
    # Handle password reset request by email
    return await password_reset_request_handler.handle_password_reset_request(payload.email)

# ---------------------------- Password Reset Confirm ----------------------------
# POST /password-reset/confirm endpoint with rate limiting
@router.post("/password-reset/confirm")
@rate_limiter_service.rate_limited("password_reset_confirm")
async def password_reset_confirm(payload: PasswordResetConfirmSchema):
    # Confirm password reset using token and new password
    return await password_reset_confirm_handler.handle_password_reset_confirm(payload.token, payload.new_password)

# ---------------------------- Account Verification Endpoint ----------------------------
# GET /verify-account endpoint with rate limiting
@router.get("/verify-account")
@rate_limiter_service.rate_limited("verify_account")
async def verify_account(token: str):
    # Verify user account using token
    return await account_verification_handler.handle_account_verification(token)
