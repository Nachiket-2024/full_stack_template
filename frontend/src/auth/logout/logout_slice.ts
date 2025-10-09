// ---------------------------- External Imports ----------------------------
// Import Redux Toolkit helpers for creating slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Import type-only PayloadAction for typing Redux actions
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Import API function to logout a single device
import { logoutApi } from "../../api/auth_api";

// Import type-only LogoutResponse for typing API response
import type { LogoutResponse } from "./logout_types";

// ---------------------------- State Type ----------------------------
// Redux state for single-device logout functionality
interface LogoutState {
    loading: boolean;              // Step 1: Indicates if logout request is in progress
    error: string | null;          // Step 2: Stores error message if request fails
    successMessage: string | null; // Step 3: Stores success message after logout completes
}

// ---------------------------- Initial State ----------------------------
const initialState: LogoutState = {
    loading: false,                // Step 1
    error: null,                   // Step 2
    successMessage: null,          // Step 3
};

// ---------------------------- Async Thunks ----------------------------
/**
 * logoutUser
 * Input: None
 * Process:
 *   1. Call API to logout current device (handles cookies)
 *   2. Return API response data if successful
 *   3. Reject with meaningful error message if API fails
 * Output: Redux async thunk with success/error payload
 */
export const logoutUser = createAsyncThunk<
    LogoutResponse,                // Return type on success
    void,                          // Argument type: none needed
    { rejectValue: string }        // Error type if rejected
>(
    "logout/logoutUser",
    async (_, thunkAPI) => {
        try {
            // Step 1: Call API
            const response = await logoutApi();

            // Step 2: Return API data
            return response.data;
        } catch (error: any) {
            // Step 3: Reject with meaningful error
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Logout failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
/**
 * logoutSlice
 * Manages single-device logout state
 * Methods:
 *   1. clearLogoutState - Reset slice to initial state
 */
const logoutSlice = createSlice({
    name: "logout",               // Step 1: Slice name
    initialState,                 // Step 2: Initial state
    reducers: {
        /**
         * clearLogoutState
         * Input: None
         * Process:
         *   1. Reset loading
         *   2. Clear error
         *   3. Clear success message
         * Output: Redux state reset to initial values
         */
        clearLogoutState: (state) => {
            state.loading = false;        // Step 1
            state.error = null;           // Step 2
            state.successMessage = null;  // Step 3
        },
    },
    extraReducers: (builder) => {
        builder
            // Pending: set loading true, clear messages
            .addCase(logoutUser.pending, (state) => {
                state.loading = true;         // Step 1
                state.error = null;           // Step 2
                state.successMessage = null;  // Step 3
            })
            // Fulfilled: stop loading, store success message
            .addCase(
                logoutUser.fulfilled,
                (state, action: PayloadAction<LogoutResponse>) => {
                    state.loading = false;                     // Step 1
                    state.successMessage = action.payload.message; // Step 2
                }
            )
            // Rejected: stop loading, store error message
            .addCase(logoutUser.rejected, (state, action) => {
                state.loading = false;                    // Step 1
                state.error = action.payload || "Logout failed"; // Step 2
            });
    },
});

// ---------------------------- Exports ----------------------------
// Export action to reset logout state
export const { clearLogoutState } = logoutSlice.actions;

// Export reducer for store integration
export default logoutSlice.reducer;
