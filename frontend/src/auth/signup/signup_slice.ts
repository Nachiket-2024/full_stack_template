// ---------------------------- External Imports ----------------------------
// Redux Toolkit functions for creating slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Type-only import for PayloadAction (needed for typing actions)
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// API wrapper for performing signup requests
import { signupApi } from "../../api/auth_api";

// Type-only imports for request and response structures
import type { SignupRequest, SignupResponse } from "./signup_types";

// ---------------------------- State Type ----------------------------
// Defines the shape of the signup slice state
interface SignupState {
    loading: boolean;              // Step 1: True while signup request is in progress
    error: string | null;          // Step 2: Stores backend or network error message
    successMessage: string | null; // Step 3: Stores success message from backend
}

// ---------------------------- Initial State ----------------------------
// Initial values for the signup slice
const initialState: SignupState = {
    loading: false,       // Step 1: No request in progress initially
    error: null,          // Step 2: No errors initially
    successMessage: null, // Step 3: No success message initially
};

// ---------------------------- Async Thunk ----------------------------
/**
 * signupUser
 * Input: SignupRequest payload containing name, email, password
 * Process:
 *   1. Call backend signup API with payload
 *   2. Return API response data if successful
 *   3. Catch errors and return meaningful reject value
 * Output: SignupResponse on success, string error message on failure
 */
export const signupUser = createAsyncThunk<
    SignupResponse,        // Type of successful response
    SignupRequest,         // Input type (signup payload)
    { rejectValue: string } // Error type if request fails
>(
    "auth/signup",
    async (payload: SignupRequest, thunkAPI) => {
        try {
            // Step 1: Call backend signup API
            const response = await signupApi(payload);

            // Step 2: Return API response data on success
            return response.data;
        } catch (error: any) {
            // Step 3: Return error message if request fails
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Signup failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
/**
 * signupSlice
 * Manages signup state in Redux store
 * Methods:
 *   1. clearSignupState - Reset loading, error, and successMessage
 */
const signupSlice = createSlice({
    name: "signup",        // Step 1: Slice name
    initialState,          // Step 2: Initial state
    reducers: {
        /**
         * clearSignupState
         * Input: None
         * Process:
         *   1. Reset loading flag
         *   2. Clear error message
         *   3. Clear success message
         * Output: Resets slice state
         */
        clearSignupState: (state) => {
            state.loading = false;        // Step 1
            state.error = null;           // Step 2
            state.successMessage = null;  // Step 3
        },
    },
    extraReducers: (builder) => {
        builder
            // Step 1: Set loading state when request is pending
            .addCase(signupUser.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.successMessage = null;
            })

            // Step 2: Handle fulfilled request
            .addCase(
                signupUser.fulfilled,
                (state, action: PayloadAction<SignupResponse>) => {
                    state.loading = false;                     // Step 2a: Stop loading
                    state.successMessage = action.payload.message; // Step 2b: Save success message
                }
            )

            // Step 3: Handle rejected request
            .addCase(signupUser.rejected, (state, action) => {
                state.loading = false;                     // Step 3a: Stop loading
                state.error = action.payload || "Signup failed"; // Step 3b: Save error message
            });
    },
});

// ---------------------------- Exports ----------------------------
// Export Redux actions
export const { clearSignupState } = signupSlice.actions;

// Export reducer for store integration
export default signupSlice.reducer;
