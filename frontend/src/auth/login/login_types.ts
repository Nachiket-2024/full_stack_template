// ---------------------------- Login Request Type ----------------------------
// Interface representing the shape of the request body for /auth/login
export interface LoginRequest {
    // User's email address
    email: string;

    // User's password
    password: string;
}

// ---------------------------- Login Response Type ----------------------------
// Interface representing the shape of the response from /auth/login
export interface LoginResponse {
    // JWT access token returned by the server
    access_token: string;

    // JWT refresh token returned by the server
    refresh_token: string;
}
