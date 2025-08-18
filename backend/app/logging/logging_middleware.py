# --- Import base class for creating custom middleware ---
from starlette.middleware.base import BaseHTTPMiddleware

# --- Import classes for handling streaming and JSON responses ---
from starlette.responses import StreamingResponse, JSONResponse

# --- Import type definitions required by Starlette middleware ---
from starlette.types import ASGIApp

# --- Import custom logger setup from logging_config module ---
from .logging_config import get_logger

# --- Initialize the logger instance using the configured logger ---
logger = get_logger()

# --- Define the custom logging middleware class that inherits from BaseHTTPMiddleware ---
class LoggingMiddleware(BaseHTTPMiddleware):
    # --- Constructor to initialize middleware with the ASGI app ---
    def __init__(self, app: ASGIApp) -> None:
        # --- Call the parent constructor with the app ---
        super().__init__(app)

    # --- This method is called for each request ---
    async def dispatch(self, request, call_next):
        # --- Log the incoming HTTP request method and URL ---
        logger.info(f"Incoming request: {request.method} {request.url}")

        try:
            # --- Process the request and get the response ---
            response = await call_next(request)
        except Exception as e:
            # --- Log any exception that occurs during request handling ---
            logger.error(f"Error processing request: {request.method} {request.url} - {str(e)}")
            # --- Return a standard 500 Internal Server Error response ---
            return JSONResponse({"detail": "Internal Server Error"}, status_code=500)

        # --- If the response is not a streaming response, log its status code ---
        if not isinstance(response, StreamingResponse):
            logger.info(f"Response: {response.status_code} for {request.method} {request.url}")

        # --- If the response is a streaming response, wrap the body to allow logging ---
        if isinstance(response, StreamingResponse):
            # --- Define an async generator to yield chunks of the streaming body ---
            async def streaming_body():
                async for chunk in response.body_iterator:
                    yield chunk

            # --- Wrap the original response in a new StreamingResponse with the same content ---
            response = StreamingResponse(
                streaming_body(), status_code=response.status_code, headers=response.headers
            )
            # --- Log the status code of the streaming response ---
            logger.info(f"Streaming response with status code: {response.status_code}")

        # --- Return the final response to the client ---
        return response
