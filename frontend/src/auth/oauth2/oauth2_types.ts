// ---------------------------- OAuth2 Login Request Type ----------------------------
// Shape of the request for initiating OAuth2 login (provider name)
export interface OAuth2LoginPayload {
    provider: "google"; // Extendable to other providers
}

// ---------------------------- OAuth2 Login Response Type ----------------------------
// Shape of the response after OAuth2 login callback
export interface OAuth2LoginResponse {
    access_token: string;    // Access token returned from backend
    refresh_token: string;   // Refresh token returned from backend
    message?: string;        // Optional success message
}
