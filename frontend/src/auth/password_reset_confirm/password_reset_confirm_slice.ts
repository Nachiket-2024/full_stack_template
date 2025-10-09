// ---------------------------- External Imports ----------------------------
// Import createSlice and createAsyncThunk from Redux Toolkit
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Type-only import for strongly-typed PayloadAction
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Import API wrapper for password reset confirmation
import { passwordResetConfirmApi } from "../../api/auth_api";

// Import types for password reset confirmation payload and response
import type {
    PasswordResetConfirmPayload,
    PasswordResetConfirmResponse,
} from "./password_reset_confirm_types";

// ---------------------------- State Type ----------------------------
// Define Redux state structure for password reset confirmation
interface PasswordResetConfirmState {
    loading: boolean;              // Step 1: True if API request is in progress
    error: string | null;          // Step 2: Stores error message if request fails
    successMessage: string | null; // Step 3: Stores success message returned by backend
}

// ---------------------------- Initial State ----------------------------
const initialState: PasswordResetConfirmState = {
    loading: false,          // Step 1
    error: null,             // Step 2
    successMessage: null,    // Step 3
};

// ---------------------------- Async Thunk ----------------------------
/**
 * confirmPasswordReset
 * Input: PasswordResetConfirmPayload containing new password and token
 * Process:
 *   1. Call API to confirm password reset
 *   2. Return response data if successful
 *   3. Handle error and reject with meaningful message
 * Output: PasswordResetConfirmResponse on success, or rejected string on error
 */
export const confirmPasswordReset = createAsyncThunk<
    PasswordResetConfirmResponse,    // Success return type
    PasswordResetConfirmPayload,     // Input payload type
    { rejectValue: string }          // Error type if rejected
>(
    "auth/passwordResetConfirm",
    async (payload, thunkAPI) => {
        try {
            // Step 1: Call API to confirm password reset
            const response = await passwordResetConfirmApi(payload);

            // Step 2: Return response data
            return response.data;
        } catch (error: any) {
            // Step 3: Return rejected value with error message
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Password reset confirmation failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
/**
 * passwordResetConfirmSlice
 * Manages state for password reset confirmation
 * Methods:
 *   1. clearPasswordResetConfirmState - Reset slice to initial state
 */
const passwordResetConfirmSlice = createSlice({
    name: "passwordResetConfirm",   // Step 1: Slice name
    initialState,                   // Step 2: Initial state
    reducers: {
        /**
         * clearPasswordResetConfirmState
         * Input: None
         * Process:
         *   1. Stop loading
         *   2. Clear error message
         *   3. Clear success message
         * Output: Redux state reset to initial values
         */
        clearPasswordResetConfirmState: (state) => {
            state.loading = false;          // Step 1
            state.error = null;             // Step 2
            state.successMessage = null;    // Step 3
        },
    },
    extraReducers: (builder) => {
        // Handle different states of the async thunk
        builder
            // Step 1: Pending state
            .addCase(confirmPasswordReset.pending, (state) => {
                state.loading = true;        // Step 1a: Set loading
                state.error = null;          // Step 1b: Clear previous errors
                state.successMessage = null; // Step 1c: Clear previous success messages
            })
            // Step 2: Fulfilled state
            .addCase(
                confirmPasswordReset.fulfilled,
                (state, action: PayloadAction<PasswordResetConfirmResponse>) => {
                    state.loading = false;                 // Step 2a: Stop loading
                    state.successMessage = action.payload.message; // Step 2b: Store success message
                }
            )
            // Step 3: Rejected state
            .addCase(confirmPasswordReset.rejected, (state, action) => {
                state.loading = false;                   // Step 3a: Stop loading
                state.error = action.payload || "Password reset confirmation failed"; // Step 3b: Store error
            });
    },
});

// ---------------------------- Exports ----------------------------
// Export action to manually clear slice state
export const { clearPasswordResetConfirmState } =
    passwordResetConfirmSlice.actions;

// Export reducer for store integration
export default passwordResetConfirmSlice.reducer;
