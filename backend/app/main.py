# ---------------------------- External Imports ----------------------------
# Load environment variables from a .env file
from dotenv import load_dotenv

# Handle file system paths in an OS-independent way
from pathlib import Path

# Import FastAPI framework and Request object for middleware/exception handling
from fastapi import FastAPI, Request

# Import CORS middleware to handle cross-origin requests
from fastapi.middleware.cors import CORSMiddleware

# Import JSONResponse to send structured error responses
from fastapi.responses import JSONResponse

# ---------------------------- Environment Setup ----------------------------
# Determine the base directory by going 3 levels up from the current file
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from the .env file located at BASE_DIR
_ = load_dotenv(dotenv_path=BASE_DIR / ".env")

# ---------------------------- Logging Setup ----------------------------
# Import custom middleware to log all API requests
from .logging.logging_middleware import LoggingMiddleware

# Import a function to get a JSON-formatted rotating logger
from .logging.logging_config import get_logger

# Initialize a logger instance for the main application
logger = get_logger("main")

# ---------------------------- Internal Imports ----------------------------
# Import authentication router
from .api.auth_routes.auth_routes import router as auth_router

# Import refresh token router for JWT/session management
from .api.auth_routes.refresh_token_routes import router as refresh_token_router

# Import admin-specific role router
from .api.role_routes.admin_routes import router as admin_router

# Import role1-specific router
from .api.role_routes.role1_routes import router as role1_router

# Import role2-specific router
from .api.role_routes.role2_routes import router as role2_router

# ---------------------------- App Initialization ----------------------------
# Create a FastAPI application instance
app = FastAPI()

# ---------------------------- Middleware Configuration ----------------------------
# Add CORS middleware to allow requests from the frontend at port 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,                   # Allow cookies and auth headers
    allow_methods=["*"],                       # Allow all HTTP methods
    allow_headers=["*"],                       # Allow all headers
)

# Add custom logging middleware to capture all requests and responses
app.add_middleware(LoggingMiddleware)

# ---------------------------- Global Exception Handler ----------------------------
# Define a handler to catch all unhandled exceptions globally
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log exception details with request URL
    logger.exception(f"Unhandled Exception at {request.url.path}: {str(exc)}")

    # Return a JSON response with HTTP status 500
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

# ---------------------------- Router Registration ----------------------------
# Register authentication router
app.include_router(auth_router)

# Register refresh token router
app.include_router(refresh_token_router)

# Register admin role router
app.include_router(admin_router)

# Register role1 router
app.include_router(role1_router)

# Register role2 router
app.include_router(role2_router)

# ---------------------------- Root Route ----------------------------
# Define a simple root endpoint to confirm the API is running
@app.get("/")
def read_root():
    return {"message": "Welcome to the Full Stack Template!"}
