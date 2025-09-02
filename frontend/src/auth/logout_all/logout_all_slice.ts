// ---------------------------- External Imports ----------------------------
// Import createSlice and createAsyncThunk from Redux Toolkit for slice creation and async actions
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Import type-only PayloadAction for typing actions in Redux state
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Import API function to perform logout from all devices
import { logoutAllApi } from "../../api/auth_api";

// Import type-only LogoutResponse for typing API response
import type { LogoutResponse } from "./logout_all_types";

// ---------------------------- State Type ----------------------------
// Define Redux state structure for logout all devices
interface LogoutAllState {
    loading: boolean;              // Indicates if the logout all request is in progress
    error: string | null;          // Stores error message if the request fails
    successMessage: string | null; // Stores success message after logout completes
}

// ---------------------------- Initial State ----------------------------
// Set initial values for the logout all devices state
const initialState: LogoutAllState = {
    loading: false,                // Not loading initially
    error: null,                   // No error initially
    successMessage: null,          // No success message initially
};

// ---------------------------- Async Thunks ----------------------------
// Define an async thunk to logout from all devices
export const logoutAllDevices = createAsyncThunk<
    LogoutResponse,                // Type of successful response
    void,                          // No argument needed for this thunk
    { rejectValue: string }        // Type of error value if rejected
>(
    "logout_all/logoutAllDevices",
    async (_, thunkAPI) => {
        try {
            // Call API to logout from all devices; backend reads cookies automatically
            const response = await logoutAllApi();
            return response.data; // Return API response data on success
        } catch (error: any) {
            // Return a reject value with error message if API call fails
            return thunkAPI.rejectWithValue(error.response?.data?.error || "Logout all devices failed");
        }
    }
);

// ---------------------------- Slice ----------------------------
// Create Redux slice for logout all devices feature
const logoutAllSlice = createSlice({
    name: "logoutAll",              // Name of the slice
    initialState,                   // Initial state defined above
    reducers: {
        // Reducer to reset logout all state to initial values
        clearLogoutAllState: (state) => {
            state.loading = false;        // Reset loading
            state.error = null;           // Clear error
            state.successMessage = null;  // Clear success message
        },
    },
    extraReducers: (builder) => {
        // Handle different states of the async thunk
        builder
            .addCase(logoutAllDevices.pending, (state) => {
                state.loading = true;      // Set loading while request is pending
                state.error = null;        // Clear previous errors
                state.successMessage = null;// Clear previous success message
            })
            .addCase(logoutAllDevices.fulfilled, (state, action: PayloadAction<LogoutResponse>) => {
                state.loading = false;                 // Stop loading
                state.successMessage = action.payload.message; // Store success message
            })
            .addCase(logoutAllDevices.rejected, (state, action) => {
                state.loading = false;                 // Stop loading
                state.error = action.payload || "Logout all devices failed"; // Store error message
            });
    },
});

// ---------------------------- Exports ----------------------------
// Export the action to clear state
export const { clearLogoutAllState } = logoutAllSlice.actions;

// Export the reducer as default for store integration
export default logoutAllSlice.reducer;
