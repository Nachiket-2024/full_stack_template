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

// Import fetchCurrentUser thunk to refresh authentication state
import { fetchCurrentUser } from "../current_user/current_user_slice";

// Import clearLoginState action to reset login slice state
import { clearLoginState } from "../login/login_slice";

// ---------------------------- State Type ----------------------------
// Redux state for "logout all devices" functionality
interface LogoutAllState {
    loading: boolean;              // Step 1: True if logout all request is in progress
    error: string | null;          // Step 2: Error message if request fails
    successMessage: string | null; // Step 3: Success message after logout completes
}

// ---------------------------- Initial State ----------------------------
// Initialize slice state
const initialState: LogoutAllState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunks ----------------------------
// logoutAllDevices: Handles logout from all devices
/**
 * Input: None
 * Process:
 *   1. Call API to logout from all devices
 *   2. Dispatch login slice reset to clear user data
 *   3. Dispatch fetchCurrentUser to update authentication state
 *   4. Return API response data if successful
 *   5. Reject with error message if API fails
 * Output: Redux async thunk with success/error payload
 */
export const logoutAllDevices = createAsyncThunk<
    LogoutResponse,
    void,
    { rejectValue: string; dispatch: any }
>(
    "logout_all/logoutAllDevices",
    async (_, thunkAPI) => {
        try {
            // Step 1: Call API
            const response = await logoutAllApi();

            // Step 2: Clear login slice state
            thunkAPI.dispatch(clearLoginState());

            // Step 3: Refresh currentUser authentication state
            await thunkAPI.dispatch(fetchCurrentUser("logoutAllThunk")).unwrap();

            // Step 4: Return API data
            return response.data;
        } catch (error: any) {
            // Step 5: Reject with meaningful error message
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Logout all devices failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
// logoutAllSlice: Manages "logout all devices" state
/**
 * Methods:
 *   1. clearLogoutAllState - Reset slice to initial state
 */
const logoutAllSlice = createSlice({
    name: "logoutAll",
    initialState,
    reducers: {
        // clearLogoutAllState: Reset slice state to initial values
        clearLogoutAllState: (state) => {
            state.loading = false;
            state.error = null;
            state.successMessage = null;
        },
    },
    extraReducers: (builder) => {
        // logoutAllDevices pending: set loading, clear previous messages
        builder.addCase(logoutAllDevices.pending, (state) => {
            state.loading = true;
            state.error = null;
            state.successMessage = null;
        });

        // logoutAllDevices fulfilled: stop loading, store success message
        builder.addCase(
            logoutAllDevices.fulfilled,
            (state, action: PayloadAction<LogoutResponse>) => {
                state.loading = false;
                state.successMessage = action.payload.message;
                state.error = null; // Ensure no error is displayed
            }
        );

        // logoutAllDevices rejected: stop loading, store error message
        builder.addCase(logoutAllDevices.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload || "Logout all devices failed";
            state.successMessage = null; // Ensure no success message is displayed
        });
    },
});

// ---------------------------- Exports ----------------------------
// Export action to reset logout all state
export const { clearLogoutAllState } = logoutAllSlice.actions;

// Export reducer for store integration
export default logoutAllSlice.reducer;
