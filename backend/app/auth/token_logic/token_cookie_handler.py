# ---------------------------- External Imports ----------------------------
# Import FastAPI's JSONResponse for typing and response handling
from fastapi.responses import JSONResponse

# ---------------------------- Token Cookie Handler Class ----------------------------
# Service class to attach access and refresh tokens as secure HTTP-only cookies to existing responses
class TokenCookieHandler:
    """
    1. set_tokens_in_cookies - Attaches access and refresh tokens as secure HTTP-only cookies to a response.
    """

    # ---------------------------- Set Tokens in Cookies ----------------------------
    def set_tokens_in_cookies(self, response: JSONResponse, tokens: dict[str, str]) -> JSONResponse:
        """
        Input:
            1. response (JSONResponse): Existing FastAPI response object to modify.
            2. tokens (dict[str, str]): Dictionary containing 'access_token' and 'refresh_token'.

        Process:
            1. Attach access token cookie with 1-hour expiry and security flags to the response.
            2. Attach refresh token cookie with 30-day expiry and security flags to the response.

        Output:
            1. JSONResponse: Same response object with cookies added.
        """
        # ---------------------------- Set Access Token Cookie ----------------------------
        response.set_cookie(
            key="access_token",                     # Cookie key name
            value=tokens["access_token"],           # Access token value
            httponly=True,                          # HTTP-only flag
            secure=True,                            # Secure flag for HTTPS
            samesite="Strict",                      # SameSite attribute
            max_age=3600                            # Expiry time in seconds (1 hour)
        )

        # ---------------------------- Set Refresh Token Cookie ----------------------------
        response.set_cookie(
            key="refresh_token",                    # Cookie key name
            value=tokens["refresh_token"],          # Refresh token value
            httponly=True,                          # HTTP-only flag
            secure=True,                            # Secure flag for HTTPS
            samesite="Strict",                      # SameSite attribute
            max_age=2592000                         # Expiry time in seconds (30 days)
        )

        # ---------------------------- Return Response ----------------------------
        return response


# ---------------------------- Singleton Instance ----------------------------
# Single global instance of TokenCookieHandler for route usage
token_cookie_handler = TokenCookieHandler()
