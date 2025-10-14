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

// Import fetchCurrentUser thunk to refresh authentication state
import { fetchCurrentUser } from "../current_user/current_user_slice";

// Import clearLoginState action to reset login slice state
import { clearLoginState } from "../login/login_slice";

// ---------------------------- State Type ----------------------------
// Redux state for single-device logout functionality
interface LogoutState {
    loading: boolean;              // Step 1: Indicates if logout request is in progress
    error: string | null;          // Step 2: Stores error message if request fails
    successMessage: string | null; // Step 3: Stores success message after logout completes
}

// ---------------------------- Initial State ----------------------------
// Initialize slice state
const initialState: LogoutState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunks ----------------------------
// logoutUser: Handles single-device logout
/**
 * Input: None
 * Process:
 *   1. Call API to logout current device
 *   2. Dispatch login slice reset to clear user data
 *   3. Dispatch fetchCurrentUser to update authentication state
 *   4. Return API response data if successful
 *   5. Reject with meaningful error message if API fails
 * Output: Redux async thunk with success/error payload
 */
export const logoutUser = createAsyncThunk<
    LogoutResponse,
    void,
    { rejectValue: string; dispatch: any }
>(
    "logout/logoutUser",
    async (_, thunkAPI) => {
        try {
            // Step 1: Call API
            const response = await logoutApi();

            // Step 2: Clear login slice state
            thunkAPI.dispatch(clearLoginState());

            // Step 3: Refresh currentUser authentication state
            await thunkAPI.dispatch(fetchCurrentUser("logoutThunk")).unwrap();

            // Step 4: Return API data
            return response.data;
        } catch (error: any) {
            // Step 5: Reject with meaningful error
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Logout failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
// logoutSlice: Manages single-device logout state
/**
 * Methods:
 *   1. clearLogoutState - Reset slice to initial state
 */
const logoutSlice = createSlice({
    name: "logout",
    initialState,
    reducers: {
        // clearLogoutState: Reset slice state to initial values
        clearLogoutState: (state) => {
            state.loading = false;
            state.error = null;
            state.successMessage = null;
        },
    },
    extraReducers: (builder) => {
        // logoutUser pending: set loading, clear previous messages
        builder.addCase(logoutUser.pending, (state) => {
            state.loading = true;
            state.error = null;
            state.successMessage = null;
        });

        // logoutUser fulfilled: stop loading, store success message
        builder.addCase(
            logoutUser.fulfilled,
            (state, action: PayloadAction<LogoutResponse>) => {
                state.loading = false;
                state.successMessage = action.payload.message;
                state.error = null; // Ensure no error is displayed
            }
        );

        // logoutUser rejected: stop loading, store error message
        builder.addCase(logoutUser.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload || "Logout failed";
            state.successMessage = null; // Ensure no success message is displayed
        });
    },
});

// ---------------------------- Exports ----------------------------
// Export action to reset logout state
export const { clearLogoutState } = logoutSlice.actions;

// Export reducer for store integration
export default logoutSlice.reducer;
