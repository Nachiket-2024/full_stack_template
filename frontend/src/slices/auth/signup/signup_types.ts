// ---------------------------- Signup Types ----------------------------

// Define the shape of the request body for signup
// This matches exactly with the backend's SignupSchema (Python Pydantic model)
export interface SignupRequest {
    // User's full name
    name: string;

    // User's email address
    email: string;

    // User's password
    password: string;
}

// Define the expected successful response from the backend
// The backend usually returns a message and maybe additional info
export interface SignupSuccessResponse {
    // Indicates that signup was successful
    message: string;

    // Optional: could include the user ID or email in some APIs
    userId?: string;

    // Optional: backend might return a verification flag
    isVerified?: boolean;
}

// Define the expected error response from the backend
export interface SignupErrorResponse {
    // General error message
    error: string;
}

// Define a union type for response, since the backend can return either success or error
export type SignupResponse = SignupSuccessResponse | SignupErrorResponse;

// Define the shape of the state managed by Redux for signup
export interface SignupState {
    // Tracks whether a signup request is in progress
    loading: boolean;

    // Stores data if signup is successful
    data: SignupSuccessResponse | null;

    // Stores error information if signup fails
    error: string | null;
}
