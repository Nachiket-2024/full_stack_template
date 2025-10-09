// ---------------------------- Signup Request Type ----------------------------
// Defines the shape of the request payload sent to /auth/signup
export interface SignupRequest {
    name: string;     // Full name of the user
    email: string;    // User email address for signup
    password: string; // Password chosen by the user
}

// ---------------------------- Signup Response Type ----------------------------
// Defines the shape of the response returned from /auth/signup
export interface SignupResponse {
    message: string;  // Success message indicating signup was successful
    user_id?: string; // Optional: ID of the newly created user
}
