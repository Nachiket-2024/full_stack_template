# ---------------------------- External Imports ----------------------------
# Import FastAPI's JSONResponse for typing and response handling
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Pydantic schema representing a pair of JWT tokens (access + refresh)
from .token_schema import TokenPairResponseSchema

# ---------------------------- Token Cookie Handler Class ----------------------------
# Service class to attach access and refresh tokens as secure HTTP-only cookies to existing responses
class TokenCookieHandler:
    """
    1. set_tokens_in_cookies - Attach access and refresh tokens as secure HTTP-only cookies to a response.
    """

    # ---------------------------- Set Tokens in Cookies ----------------------------
    def set_tokens_in_cookies(
        self, response: JSONResponse, tokens: TokenPairResponseSchema
    ) -> JSONResponse:
        """
        Input:
            1. response (JSONResponse): Existing FastAPI response object to modify.
            2. tokens (TokenPairResponseSchema): Pydantic model containing 'access_token' and 'refresh_token'.

        Process:
            1. Extract access_token and refresh_token from the Pydantic model.
            2. Attach access token as HTTP-only, secure, SameSite=Strict cookie with 1-hour expiry.
            3. Attach refresh token as HTTP-only, secure, SameSite=Strict cookie with 30-day expiry.
            4. Return the modified response object.

        Output:
            1. JSONResponse: Same response object with access and refresh cookies set.
        """

        # Step 1: Extract tokens from Pydantic model
        access_token = tokens.access_token
        refresh_token = tokens.refresh_token

        # Step 2: Attach access token as HTTP-only, secure, SameSite=Strict cookie with 1-hour expiry
        response.set_cookie(
            key="access_token",      # Cookie key name
            value=access_token,      # Assign access token value
            httponly=True,           # HTTP-only flag
            secure=True,             # Secure flag for HTTPS
            samesite="Strict",       # SameSite attribute
            max_age=3600             # Expiry time in seconds (1 hour)
        )

        # Step 3: Attach refresh token as HTTP-only, secure, SameSite=Strict cookie with 30-day expiry
        response.set_cookie(
            key="refresh_token",     # Cookie key name
            value=refresh_token,     # Assign refresh token value
            httponly=True,           # HTTP-only flag
            secure=True,             # Secure flag for HTTPS
            samesite="Strict",       # SameSite attribute
            max_age=2592000          # Expiry time in seconds (30 days)
        )

        # Step 4: Return the modified response object
        return response


# ---------------------------- Singleton Instance ----------------------------
# Single global instance of TokenCookieHandler for consistent cookie handling across routes
token_cookie_handler = TokenCookieHandler()
