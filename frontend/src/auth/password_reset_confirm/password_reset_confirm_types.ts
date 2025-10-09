// ---------------------------- Password Reset Confirm Request Type ----------------------------
// Shape of the request body for /auth/password-reset/confirm
export interface PasswordResetConfirmPayload {
    // Token received by email to verify the reset request
    token: string;

    // New password that the user wants to set
    new_password: string;
}

// ---------------------------- Password Reset Confirm Response Type ----------------------------
// Shape of the response returned from /auth/password-reset/confirm
export interface PasswordResetConfirmResponse {
    // Success message if password reset is successful
    message: string;
}
