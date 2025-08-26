// ---------------------------- Password Reset Request Type ----------------------------
// Shape of the request body for /auth/password-reset/request
export interface PasswordResetRequestPayload {
    email: string; // User email to send password reset link
}

// ---------------------------- Password Reset Request Response Type ----------------------------
// Shape of the response from /auth/password-reset/request
export interface PasswordResetRequestResponse {
    message: string; // Success message indicating email was sent
}
