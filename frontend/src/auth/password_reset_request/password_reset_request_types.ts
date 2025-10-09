// ---------------------------- Password Reset Request Type ----------------------------
// Defines the shape of the request body sent to /auth/password-reset/request
export interface PasswordResetRequestPayload {
    // Email of the user to receive the password reset link
    email: string;
}

// ---------------------------- Password Reset Request Response Type ----------------------------
// Defines the expected shape of the response from /auth/password-reset/request
export interface PasswordResetRequestResponse {
    // Success message indicating that the password reset email was sent
    message: string;
}
