// ---------------------------- Account Verification Request Type ----------------------------
// Shape of the request to verify account via token and email
export interface VerifyAccountPayload {
    token: string;
    email: string;
}

// ---------------------------- Account Verification Response Type ----------------------------
// Shape of the response from backend after verification
export interface VerifyAccountResponse {
    message: string; // Success message
}
