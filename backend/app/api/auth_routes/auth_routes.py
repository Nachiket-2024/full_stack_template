# ---------------------------- External Imports ----------------------------
# FastAPI router for grouping endpoints, Depends for dependency injection, and response handling
from fastapi import APIRouter, Depends

# Responses for JSON and HTTP redirects
from fastapi.responses import JSONResponse, RedirectResponse

# Async SQLAlchemy session for database interactions
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Signup request/response schema
from ...auth.signup.signup_schema import SignupSchema

# Login request/response schema
from ...auth.login.login_schema import LoginSchema

# Password reset confirmation schema
from ...auth.password_reset_confirm.password_reset__confirm_schema import PasswordResetConfirmSchema

# Password reset request schema
from ...auth.password_reset_request.password_reset_request_schema import PasswordResetRequestSchema

# Refresh token schema
from ...auth.token_logic.refresh_token_schema import RefreshTokenSchema

# Signup handler to process user registration
from ...auth.signup.signup_handler import signup_handler

# Login handler to authenticate users
from ...auth.login.login_handler import login_handler

# OAuth2 login handler for third-party authentication
from ...auth.oauth2.oauth2_login_handler import oauth2_login_handler

# Password reset request handler
from ...auth.password_reset_request.password_reset_request_handler import password_reset_request_handler

# Password reset confirmation handler
from ...auth.password_reset_confirm.password_reset_confirm_handler import password_reset_confirm_handler

# Logout handler
from ...auth.logout.logout_handler import logout_handler

# Logout all devices handler
from ...auth.logout.logout_all_handler import logout_all_handler

# Account verification handler
from ...auth.verify_account.account_verification_handler import account_verification_handler

# Rate limiter service to prevent abuse of endpoints
from ...auth.security.rate_limiter_service import rate_limiter_service

# Login protection service for failed login attempt tracking
from ...auth.security.login_protection_service import login_protection_service

# JWT service for token handling
from ...auth.token_logic.jwt_service import jwt_service

# Application settings like URLs and client IDs
from ...core.settings import settings

# Database connection abstraction for getting async sessions
from ...database.connection import database

# ---------------------------- Router ----------------------------
# Create a FastAPI router with /auth prefix and authentication-related tag
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------- Signup Endpoint ----------------------------
# POST /signup endpoint with rate limiting
@router.post("/signup")
@rate_limiter_service.rate_limited("signup")
async def signup(payload: SignupSchema, db: AsyncSession = Depends(database.get_session)):

    # Handle user signup and get response and HTTP status
    response, status = await signup_handler.handle_signup(payload.name, payload.email, payload.password, db=db)
    # Return JSON response with the result and status
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Login Endpoint ----------------------------
# POST /login endpoint with rate limiting
@router.post("/login")
@rate_limiter_service.rate_limited("login")
async def login(payload: LoginSchema, db: AsyncSession = Depends(database.get_session)):

    # Key to track login attempts per email
    email_lock_key = f"login_lock:email:{payload.email}"
    # Handle login and get response and HTTP status
    response, status = await login_handler.handle_login(payload.email, payload.password, db=db)

    # Check if the login action is allowed (rate limiting / lockout)
    allowed = await login_protection_service.check_and_record_action(email_lock_key, success=(status==200))
    # If too many failed attempts, return 429 error
    if not allowed:
        return JSONResponse(content={"error": "Too many failed login attempts, account temporarily locked"}, status_code=429)

    # ---------------------------- Set Tokens in HTTP-only Cookies ----------------------------
    # Create JSON response with the original content
    resp = JSONResponse(content=response, status_code=status)

    # Set access token cookie (1 hour expiry)
    resp.set_cookie(
        key="access_token",
        value=response["access_token"],  # Make sure the login handler returns 'access_token' in response
        httponly=True,
        secure=True,       # Only send over HTTPS
        samesite="Strict", # Prevent cross-site request sending
        max_age=3600       # 1 hour
    )

    # Set refresh token cookie (30 days expiry)
    resp.set_cookie(
        key="refresh_token",
        value=response["refresh_token"],  # Make sure the login handler returns 'refresh_token'
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=2592000   # 30 days
    )

    return resp

# ---------------------------- OAuth2 Google Login Initiation ----------------------------
# GET /oauth2/login/google endpoint to initiate Google OAuth2 login
@router.get("/oauth2/login/google")
@rate_limiter_service.rate_limited("oauth2_login")
async def oauth2_login_google():

    # Base URL for Google OAuth2 authorization
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    # Scopes requested from Google
    scopes = "openid email profile"
    # Redirect URL after successful authorization
    redirect_uri = f"{settings.BACKEND_BASE_URL}/auth/oauth2/callback/google"

    # Construct full Google OAuth2 authorization URL
    auth_url = (
        f"{google_auth_url}?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scopes.replace(' ', '%20')}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    # Redirect the client to Google's authorization page
    return RedirectResponse(url=auth_url)

# ---------------------------- OAuth2 Google Callback ----------------------------
@router.get("/oauth2/callback/google")
@rate_limiter_service.rate_limited("oauth2_callback")
async def oauth2_callback_google(code: str):

    # Handle OAuth2 login using the code and get JWT tokens
    jwt_tokens, status = await oauth2_login_handler.handle_oauth2_login({"code": code})

    # If login failed, redirect to failure page
    if status != 200:
        return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/oauth2-failure?error=login_failed")

    # ---------------------------- Set Tokens in HTTP-only Cookies ----------------------------
    response = RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/oauth2-success")
    
    # Access token (1 hour expiry)
    response.set_cookie(
        key="access_token",
        value=jwt_tokens["access_token"],
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=3600
    )

    # Refresh token (30 days expiry)
    response.set_cookie(
        key="refresh_token",
        value=jwt_tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=2592000
    )

    return response

# ---------------------------- Logout Endpoint ----------------------------
@router.post("/logout")
@rate_limiter_service.rate_limited("logout")
async def logout(payload: RefreshTokenSchema, db: AsyncSession = Depends(database.get_session)):
    
    # Handle logout and invalidate refresh token in backend
    response, status = await logout_handler.handle_logout(payload.refresh_token, db=db)
    
    # ---------------------------- Clear HTTP-only Cookies ----------------------------
    resp = JSONResponse(content=response, status_code=status)
    
    # Remove access token cookie
    resp.delete_cookie(key="access_token", httponly=True, secure=True, samesite="Strict")
    
    # Remove refresh token cookie
    resp.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="Strict")
    
    return resp

# ---------------------------- Logout All Devices Endpoint ----------------------------
@router.post("/logout/all")
@rate_limiter_service.rate_limited("logout_all")
async def logout_all(payload: RefreshTokenSchema, db: AsyncSession = Depends(database.get_session)):
    
    # Revoke all refresh tokens for the user
    response, status = await logout_all_handler.handle_logout_all(payload.refresh_token, db=db)
    
    # ---------------------------- Clear HTTP-only Cookies ----------------------------
    resp = JSONResponse(content=response, status_code=status)
    
    # Remove access token cookie
    resp.delete_cookie(key="access_token", httponly=True, secure=True, samesite="Strict")
    
    # Remove refresh token cookie
    resp.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="Strict")
    
    return resp

# ---------------------------- Password Reset Request ----------------------------
# POST /password-reset/request endpoint with rate limiting
@router.post("/password-reset/request")
@rate_limiter_service.rate_limited("password_reset_request")
async def password_reset_request(payload: PasswordResetRequestSchema, db: AsyncSession = Depends(database.get_session)):

    # Handle password reset request and send email
    response, status = await password_reset_request_handler.handle_password_reset_request(payload.email, db=db)
    # Return JSON response
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Password Reset Confirm ----------------------------
# POST /password-reset/confirm endpoint with rate limiting
@router.post("/password-reset/confirm")
@rate_limiter_service.rate_limited("password_reset_confirm")
async def password_reset_confirm(payload: PasswordResetConfirmSchema, db: AsyncSession = Depends(database.get_session)):

    # Verify the token and extract payload
    token_payload = await jwt_service.verify_token(payload.token)

    # Return error if token is invalid or expired
    if not token_payload or "email" not in token_payload:
        return JSONResponse(content={"error": "Invalid or expired token"}, status_code=400)

    # Get user's email from token payload
    email = token_payload["email"]

    # Prepare a Redis key to track password reset attempts for this email
    email_lock_key = f"login_lock:email:{email}"

    # Handle password reset confirmation
    response, status = await password_reset_confirm_handler.handle_password_reset_confirm(payload.token, payload.new_password, db=db)

    # Check if action is allowed (prevent brute-force)
    allowed = await login_protection_service.check_and_record_action(email_lock_key, success=(status==200))
    # Return error if too many failed attempts
    if not allowed:
        return JSONResponse(content={"error": "Too many failed attempts, temporarily locked"}, status_code=429)

    # Return JSON response
    return JSONResponse(content=response, status_code=status)

# ---------------------------- Account Verification Endpoint ----------------------------
# GET /verify-account endpoint with rate limiting
@router.get("/verify-account")
@rate_limiter_service.rate_limited("verify_account")
async def verify_account(token: str, email: str, db: AsyncSession = Depends(database.get_session)):

    # Key to track account verification attempts per email
    email_lock_key = f"login_lock:email:{email}"
    # Handle account verification
    response, status = await account_verification_handler.handle_account_verification(token, db=db)

    # Check if action is allowed
    allowed = await login_protection_service.check_and_record_action(email_lock_key, success=(status==200))
    # Return error if too many failed attempts
    if not allowed:
        return JSONResponse(content={"error": "Too many failed attempts, account temporarily locked"}, status_code=429)

    # Return JSON response
    return JSONResponse(content=response, status_code=status)
