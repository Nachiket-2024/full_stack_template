# ---------------------------- External Imports ----------------------------
# Import FastAPI's JSONResponse for HTTP response handling
from fastapi.responses import JSONResponse

# ---------------------------- Token Cookie Handler ----------------------------
class TokenCookieHandler:

    # ---------------------------- Set Tokens in Cookies ----------------------------
    @staticmethod
    def set_tokens_in_cookies(tokens: dict[str, str]) -> JSONResponse:
        # Create base JSON response
        response = JSONResponse(content={"message": "Tokens issued successfully"})

        # Access token (1 hour expiry)
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=3600  # 1 hour
        )

        # Refresh token (30 days expiry)
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=2592000  # 30 days
        )

        # Return response with cookies set
        return response


# ---------------------------- Singleton Instance ----------------------------
token_cookie_handler = TokenCookieHandler()
