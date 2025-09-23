# ---------------------------- External Imports ----------------------------
# Base class for creating custom Starlette middleware
from starlette.middleware.base import BaseHTTPMiddleware

# Classes for handling streaming and JSON responses
from starlette.responses import StreamingResponse, JSONResponse

# Type definitions required by Starlette middleware
from starlette.types import ASGIApp  # Type hint for ASGI app

# ---------------------------- Internal Imports ----------------------------
# Import custom logger setup from local logging configuration
from .logging_config import get_logger  # Logger configuration

# ---------------------------- Logger Initialization ----------------------------
# Initialize the logger instance using the configured logger
logger = get_logger()  # Module-specific logger

# ---------------------------- Custom Logging Middleware Class ----------------------------
# Middleware to log HTTP requests and responses, including streaming
class LoggingMiddleware(BaseHTTPMiddleware):
    """
    1. __init__ - Initialize middleware with ASGI app.
    2. dispatch - Log HTTP requests and responses, handle exceptions.
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize middleware with ASGI app
    def __init__(self, app: ASGIApp) -> None:
        """
        Input:
            1. app (ASGIApp): The Starlette ASGI application instance.
        
        Process:
            1. Call the parent BaseHTTPMiddleware constructor with the app to initialize middleware.

        Output:
            1. None
        """
        # Step 1: Call parent constructor to initialize middleware with ASGI app
        super().__init__(app)  

    # ---------------------------- Dispatch Method ----------------------------
    # Override dispatch to log requests and responses
    async def dispatch(self, request, call_next):
        """
        Input:
            1. request: Incoming HTTP request object.
            2. call_next: Callable to forward request to the next middleware/endpoint.

        Process:
            1. Process the request by calling next middleware or endpoint, handle exceptions.
            2. Wrap streaming responses to preserve the streaming body.
            3. Return the final response object to the client.

        Output:
            1. Response object (JSONResponse or StreamingResponse) to return to client.
        """
        # Log the incoming HTTP request method and URL
        logger.info(f"Incoming request: {request.method} {request.url}")

        try:
            # Step 1: Process the request by calling next middleware or endpoint, handle exceptions
            response = await call_next(request)

        except Exception as e:
            # Log exception details with request context
            logger.error(f"Error processing request: {request.method} {request.url} - {str(e)}")

            # Return JSONResponse with 500 Internal Server Error
            return JSONResponse(
                {"detail": "Internal Server Error"},
                status_code=500
            )

        # Log standard (non-streaming) response status
        if not isinstance(response, StreamingResponse):
            logger.info(
                f"Response: {response.status_code} for {request.method} {request.url}"
            )

        # Step 2: Handle streaming responses
        if isinstance(response, StreamingResponse):

            # Step 2a: Async generator to wrap streaming body
            async def streaming_body():
                async for chunk in response.body_iterator:
                    yield chunk  # Yield each chunk to preserve streaming

            # Step 2b: Recreate StreamingResponse with same status and headers
            response = StreamingResponse(
                streaming_body(),  # Async generator as body
                status_code=response.status_code,  # Preserve status code
                headers=response.headers  # Preserve headers
            )

            # Log the streaming response status code
            logger.info(f"Streaming response with status code: {response.status_code}")

        # Step 3: Return the final response object to the client
        return response
