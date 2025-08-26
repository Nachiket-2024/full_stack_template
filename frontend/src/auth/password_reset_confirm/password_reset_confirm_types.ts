// ---------------------------- Password Reset Confirm Request Type ----------------------------
// Shape of the request body for /auth/password-reset/confirm
export interface PasswordResetConfirmPayload {
    token: string;        // Token received via email
    new_password: string; // New password user wants to set
}

// ---------------------------- Password Reset Confirm Response Type ----------------------------
// Shape of the response from /auth/password-reset/confirm
export interface PasswordResetConfirmResponse {
    message: string; // Success message if password reset is successful
}
