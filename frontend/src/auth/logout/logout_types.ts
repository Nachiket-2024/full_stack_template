// ---------------------------- Logout Request Type ----------------------------
// Shape of the request body for /auth/logout and /auth/logout/all
export interface LogoutPayload {
    refresh_token: string; // Refresh token to invalidate
}

// ---------------------------- Logout Response Type ----------------------------
// Shape of the response from /auth/logout or /auth/logout/all
export interface LogoutResponse {
    message: string; // Success message
}
