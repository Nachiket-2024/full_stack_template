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
class LoggingMiddleware(BaseHTTPMiddleware):
    """
    1. __init__ - Initialize middleware with ASGI app.
    2. dispatch - Log HTTP requests and responses, handle exceptions.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self, app: ASGIApp) -> None:
        """
        Input:
            1. app (ASGIApp): The Starlette ASGI application instance.
        
        Process:
            1. Call the parent BaseHTTPMiddleware constructor with the app.

        Output:
            1. None
        """
        # Call the parent constructor with the app
        super().__init__(app)

    # ---------------------------- Dispatch Method ----------------------------
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
        # ---------------------------- Log Incoming Request ----------------------------
        logger.info(f"Incoming request: {request.method} {request.url}")

        try:
            # ---------------------------- Process Request ----------------------------
            response = await call_next(request)
        except Exception as e:
            # ---------------------------- Exception Handling ----------------------------
            logger.error(f"Error processing request: {request.method} {request.url} - {str(e)}")
            return JSONResponse({"detail": "Internal Server Error"}, status_code=500)

        # ---------------------------- Log Standard Response ----------------------------
        if not isinstance(response, StreamingResponse):
            logger.info(f"Response: {response.status_code} for {request.method} {request.url}")

        # ---------------------------- Wrap Streaming Response ----------------------------
        if isinstance(response, StreamingResponse):

            # ---------------------------- Streaming Body Wrapper ----------------------------
            async def streaming_body():
                async for chunk in response.body_iterator:
                    yield chunk

            # Recreate streaming response with same status and headers
            response = StreamingResponse(
                streaming_body(), status_code=response.status_code, headers=response.headers
            )

            # Log streaming response status code
            logger.info(f"Streaming response with status code: {response.status_code}")

        # ---------------------------- Return Response ----------------------------
        return response
