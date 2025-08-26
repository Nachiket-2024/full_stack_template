// ---------------------------- Login Request Type ----------------------------
// Shape of the request body for /auth/login
export interface LoginRequest {
    email: string;
    password: string;
}

// ---------------------------- Login Response Type ----------------------------
// Shape of the response from /auth/login
export interface LoginResponse {
    access_token: string;
    refresh_token: string;
}
