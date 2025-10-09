// ---------------------------- External Imports ----------------------------
// Redux Toolkit functions for creating slices and async actions
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Type-only import for strongly-typed Redux actions
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// API wrapper function to request a password reset
import { passwordResetRequestApi } from "../../api/auth_api";

// Type definitions for request payload and response from API
import type {
    PasswordResetRequestPayload,
    PasswordResetRequestResponse,
} from "./password_reset_request_types";

// ---------------------------- State Type ----------------------------
// Structure of Redux state for password reset request
interface PasswordResetRequestState {
    loading: boolean;              // Step 1: True when request is in progress
    error: string | null;          // Step 2: Stores error message if request fails
    successMessage: string | null; // Step 3: Stores success message from backend
}

// ---------------------------- Initial State ----------------------------
// Default values for the Redux slice state
const initialState: PasswordResetRequestState = {
    loading: false,                // Step 1
    error: null,                   // Step 2
    successMessage: null,          // Step 3
};

// ---------------------------- Async Thunk ----------------------------
/**
 * requestPasswordReset
 * Input:
 *   payload: PasswordResetRequestPayload containing user email
 * Process:
 *   1. Call API to request password reset
 *   2. Return API response data if successful
 *   3. Handle API error and reject with meaningful message
 * Output:
 *   PasswordResetRequestResponse on success, or rejected string on error
 */
export const requestPasswordReset = createAsyncThunk<
    PasswordResetRequestResponse,   // Success return type
    PasswordResetRequestPayload,    // Input argument type
    { rejectValue: string }         // Type of error returned if rejected
>(
    "auth/passwordResetRequest",
    async (payload, thunkAPI) => {
        try {
            // Step 1: Call API to request password reset
            const response = await passwordResetRequestApi(payload);

            // Step 2: Return API response data if successful
            return response.data;
        } catch (error: any) {
            // Step 3: Handle API error and reject with meaningful message
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Password reset request failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
/**
 * passwordResetRequestSlice
 * Manages state for password reset request
 * Methods:
 *   1. clearPasswordResetRequestState - Reset slice to initial state
 */
const passwordResetRequestSlice = createSlice({
    name: "passwordResetRequest",  // Step 1: Slice name
    initialState,                  // Step 2: Initial state
    reducers: {
        /**
         * clearPasswordResetRequestState
         * Input: None
         * Process:
         *   1. Stop loading
         *   2. Clear error message
         *   3. Clear success message
         * Output: Redux state reset to initial values
         */
        clearPasswordResetRequestState: (state) => {
            state.loading = false;           // Step 1
            state.error = null;              // Step 2
            state.successMessage = null;     // Step 3
        },
    },
    extraReducers: (builder) => {
        // Handle different states of the async thunk
        builder
            // Step 1: Pending state
            .addCase(requestPasswordReset.pending, (state) => {
                state.loading = true;           // Step 1a: Set loading
                state.error = null;             // Step 1b: Clear previous errors
                state.successMessage = null;    // Step 1c: Clear previous success messages
            })
            // Step 2: Fulfilled state
            .addCase(
                requestPasswordReset.fulfilled,
                (state, action: PayloadAction<PasswordResetRequestResponse>) => {
                    state.loading = false;                 // Step 2a: Stop loading
                    state.successMessage = action.payload.message; // Step 2b: Store success message
                }
            )
            // Step 3: Rejected state
            .addCase(requestPasswordReset.rejected, (state, action) => {
                state.loading = false;                 // Step 3a: Stop loading
                state.error = action.payload || "Password reset request failed"; // Step 3b: Store error
            });
    },
});

// ---------------------------- Exports ----------------------------
// Export the action to clear state manually
export const { clearPasswordResetRequestState } =
    passwordResetRequestSlice.actions;

// Export reducer for store integration
export default passwordResetRequestSlice.reducer;
