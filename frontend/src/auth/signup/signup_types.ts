// ---------------------------- Signup Request Type ----------------------------
// Shape of the request body for /auth/signup
export interface SignupRequest {
    name: string;
    email: string;
    password: string;
}

// ---------------------------- Signup Response Type ----------------------------
// Shape of the response from /auth/signup
export interface SignupResponse {
    message: string;          // Success message
    user_id?: string;         // Optional ID of the newly created user
}
