# ---------------------------- External Imports ----------------------------
# Import FastAPI's JSONResponse for HTTP response handling
from fastapi.responses import JSONResponse

# ---------------------------- Token Cookie Handler Class ----------------------------
# Service class to set access and refresh tokens in HTTP-only cookies
class TokenCookieHandler:
    """
    1. set_tokens_in_cookies - Sets access and refresh tokens in secure HTTP-only cookies and returns JSONResponse.
    """

    # ---------------------------- Set Tokens in Cookies ----------------------------
    @staticmethod
    def set_tokens_in_cookies(tokens: dict[str, str]) -> JSONResponse:
        """
        Input:
            1. tokens (dict[str, str]): Dictionary containing 'access_token' and 'refresh_token'.

        Process:
            1. Create a base JSONResponse with a success message.
            2. Set access token cookie with 1-hour expiry and security flags.
            3. Set refresh token cookie with 30-day expiry and security flags.

        Output:
            1. JSONResponse: Response object with cookies set.
        """
        # ---------------------------- Create Base Response ----------------------------
        response = JSONResponse(content={"message": "Tokens issued successfully"})

        # ---------------------------- Set Access Token Cookie ----------------------------
        response.set_cookie(
            key="access_token",                     # Cookie key name
            value=tokens["access_token"],           # Cookie value from input tokens
            httponly=True,                          # HTTP-only flag
            secure=True,                            # Secure flag
            samesite="Strict",                      # SameSite attribute
            max_age=3600                             # 1 hour expiry in seconds
        )

        # ---------------------------- Set Refresh Token Cookie ----------------------------
        response.set_cookie(
            key="refresh_token",                    # Cookie key name
            value=tokens["refresh_token"],          # Cookie value from input tokens
            httponly=True,                          # HTTP-only flag
            secure=True,                            # Secure flag
            samesite="Strict",                      # SameSite attribute
            max_age=2592000                          # 30 days expiry in seconds
        )

        # ---------------------------- Return Response ----------------------------
        return response


# ---------------------------- Singleton Instance ----------------------------
# Single global instance of TokenCookieHandler for route usage
token_cookie_handler = TokenCookieHandler()
