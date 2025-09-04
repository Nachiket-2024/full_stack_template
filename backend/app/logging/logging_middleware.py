# ---------------------------- External Imports ----------------------------
# Base class for creating custom Starlette middleware
from starlette.middleware.base import BaseHTTPMiddleware

# Classes for handling streaming and JSON responses
from starlette.responses import StreamingResponse, JSONResponse

# Type definitions required by Starlette middleware
from starlette.types import ASGIApp

# ---------------------------- Internal Imports ----------------------------
# Import custom logger setup from local logging configuration
from .logging_config import get_logger

# ---------------------------- Logger Initialization ----------------------------
# Initialize the logger instance using the configured logger
logger = get_logger()

# ---------------------------- Custom Logging Middleware Class ----------------------------
# Define a custom middleware class to log HTTP requests and responses
class LoggingMiddleware(BaseHTTPMiddleware):
    
    # ---------------------------- Constructor ----------------------------
    # Initialize middleware with the ASGI app
    def __init__(self, app: ASGIApp) -> None:
        # Call the parent constructor with the app
        super().__init__(app)

    # ---------------------------- Dispatch Method ----------------------------
    # Called for each incoming HTTP request
    async def dispatch(self, request, call_next):
        # Log the incoming HTTP request method and URL
        logger.info(f"Incoming request: {request.method} {request.url}")

        try:
            # Process the request and get the response
            response = await call_next(request)
        except Exception as e:
            # Log any exception that occurs during request handling
            logger.error(f"Error processing request: {request.method} {request.url} - {str(e)}")
            # Return a standard 500 Internal Server Error response
            return JSONResponse({"detail": "Internal Server Error"}, status_code=500)

        # If the response is not a streaming response, log its status code
        if not isinstance(response, StreamingResponse):
            logger.info(f"Response: {response.status_code} for {request.method} {request.url}")

        # If the response is a streaming response, wrap the body to allow logging
        if isinstance(response, StreamingResponse):

            # ---------------------------- Streaming Body Wrapper ----------------------------
            # Define an async generator to yield chunks of the streaming body
            async def streaming_body():
                async for chunk in response.body_iterator:
                    yield chunk

            # Wrap the original response in a new StreamingResponse with the same content
            response = StreamingResponse(
                streaming_body(), status_code=response.status_code, headers=response.headers
            )
            # Log the status code of the streaming response
            logger.info(f"Streaming response with status code: {response.status_code}")

        # Return the final response to the client
        return response
