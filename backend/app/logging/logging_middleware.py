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
            1. Call the parent BaseHTTPMiddleware constructor with the app.

        Output:
            1. None
        """
        # Call parent constructor to initialize middleware with ASGI app
        super().__init__(app)  

    # ---------------------------- Dispatch Method ----------------------------
    # Override dispatch to log requests and responses
    async def dispatch(self, request, call_next):
        """
        Input:
            1. request: Incoming HTTP request object.
            2. call_next: Callable to forward request to the next middleware/endpoint.

        Process:
            1. Log the incoming request method and URL.
            2. Process the request and capture response, handle exceptions.
            3. Log status code for standard responses.
            4. Wrap streaming responses to allow logging of body chunks.
            5. Log streaming response status code.

        Output:
            1. Response object (JSONResponse or StreamingResponse) to return to client.
        """
        # Log the incoming HTTP request method and URL
        logger.info(f"Incoming request: {request.method} {request.url}")

        try:
            # Call the next middleware or endpoint to process the request
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

        # Handle streaming responses
        if isinstance(response, StreamingResponse):

            # Async generator to wrap streaming body
            async def streaming_body():
                async for chunk in response.body_iterator:
                    yield chunk  # Yield each chunk to preserve streaming

            # Recreate StreamingResponse with same status and headers
            response = StreamingResponse(
                streaming_body(),  # Async generator as body
                status_code=response.status_code,  # Preserve status code
                headers=response.headers  # Preserve headers
            )

            # Log the streaming response status code
            logger.info(f"Streaming response with status code: {response.status_code}")

        # Return the final response object to the client
        return response  
