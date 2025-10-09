// ---------------------------- External Imports ----------------------------
// Import Redux Toolkit helpers for creating slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Import type-only PayloadAction for typing Redux actions
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Import API function to logout from all devices
import { logoutAllApi } from "../../api/auth_api";

// Import type-only LogoutResponse for typing API response
import type { LogoutResponse } from "./logout_all_types";

// ---------------------------- State Type ----------------------------
// Redux state for "logout all devices" functionality
interface LogoutAllState {
    loading: boolean;              // Step 1: True if logout all request is in progress
    error: string | null;          // Step 2: Error message if request fails
    successMessage: string | null; // Step 3: Success message after logout completes
}

// ---------------------------- Initial State ----------------------------
const initialState: LogoutAllState = {
    loading: false,                // Step 1
    error: null,                   // Step 2
    successMessage: null,          // Step 3
};

// ---------------------------- Async Thunks ----------------------------
/**
 * logoutAllDevices
 * Input: None
 * Process:
 *   1. Call API to logout from all devices
 *   2. Return API response data if successful
 *   3. Reject with error message if API fails
 * Output: Redux async thunk with success/error payload
 */
export const logoutAllDevices = createAsyncThunk<
    LogoutResponse,                // Return type on success
    void,                          // Argument type: none needed
    { rejectValue: string }        // Error type if rejected
>(
    "logout_all/logoutAllDevices",
    async (_, thunkAPI) => {
        try {
            // Step 1: Call API
            const response = await logoutAllApi();

            // Step 2: Return API data
            return response.data;
        } catch (error: any) {
            // Step 3: Reject with meaningful error message
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Logout all devices failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
/**
 * logoutAllSlice
 * Manages "logout all devices" state
 * Methods:
 *   1. clearLogoutAllState - Reset slice to initial state
 */
const logoutAllSlice = createSlice({
    name: "logoutAll",              // Step 1: Slice name
    initialState,                   // Step 2: Initial state
    reducers: {
        /**
         * clearLogoutAllState
         * Input: None
         * Process:
         *   1. Reset loading
         *   2. Clear error
         *   3. Clear success message
         * Output: Redux state reset to initial values
         */
        clearLogoutAllState: (state) => {
            state.loading = false;        // Step 1
            state.error = null;           // Step 2
            state.successMessage = null;  // Step 3
        },
    },
    extraReducers: (builder) => {
        builder
            // Pending: set loading true, clear messages
            .addCase(logoutAllDevices.pending, (state) => {
                state.loading = true;          // Step 1
                state.error = null;            // Step 2
                state.successMessage = null;   // Step 3
            })
            // Fulfilled: stop loading, store success message
            .addCase(
                logoutAllDevices.fulfilled,
                (state, action: PayloadAction<LogoutResponse>) => {
                    state.loading = false;                    // Step 1
                    state.successMessage = action.payload.message; // Step 2
                }
            )
            // Rejected: stop loading, store error message
            .addCase(logoutAllDevices.rejected, (state, action) => {
                state.loading = false;                    // Step 1
                state.error = action.payload || "Logout all devices failed"; // Step 2
            });
    },
});

// ---------------------------- Exports ----------------------------
// Export action to reset slice
export const { clearLogoutAllState } = logoutAllSlice.actions;

// Export reducer for store integration
export default logoutAllSlice.reducer;
