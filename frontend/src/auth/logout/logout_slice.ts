// ---------------------------- External Imports ----------------------------
// Import createSlice and createAsyncThunk for Redux logic
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Import type-only PayloadAction for Redux state typing
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Import API functions instead of calling axios directly
import { logoutApi, logoutAllApi } from "../../api/auth_api";

// Import type-only API request/response types for logout
import type { LogoutPayload, LogoutResponse } from "./logout_types";

// ---------------------------- State Type ----------------------------
// Redux state specific to logout flow
interface LogoutState {
    loading: boolean;            // Is logout request in progress
    error: string | null;        // Error message if request fails
    successMessage: string | null; // Message on successful logout
}

// ---------------------------- Initial State ----------------------------
const initialState: LogoutState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunks ----------------------------

// Logout single device
export const logoutUser = createAsyncThunk<
    LogoutResponse,
    LogoutPayload,
    { rejectValue: string }
>("auth/logout", async (payload, thunkAPI) => {
    try {
        // Call logout API
        const response = await logoutApi(payload);
        return response.data;
    } catch (error: any) {
        return thunkAPI.rejectWithValue(error.response?.data?.error || "Logout failed");
    }
});

// Logout all devices
export const logoutAllDevices = createAsyncThunk<
    LogoutResponse,
    LogoutPayload,
    { rejectValue: string }
>("auth/logoutAll", async (payload, thunkAPI) => {
    try {
        // Call logout all API
        const response = await logoutAllApi(payload);
        return response.data;
    } catch (error: any) {
        return thunkAPI.rejectWithValue(error.response?.data?.error || "Logout all devices failed");
    }
});

// ---------------------------- Slice ----------------------------
const logoutSlice = createSlice({
    name: "logout",
    initialState,
    reducers: {
        // Reset logout state (useful after showing toast/alert)
        clearLogoutState: (state) => {
            state.loading = false;
            state.error = null;
            state.successMessage = null;
        },
    },
    extraReducers: (builder) => {
        builder
            // Logout single device
            .addCase(logoutUser.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.successMessage = null;
            })
            .addCase(logoutUser.fulfilled, (state, action: PayloadAction<LogoutResponse>) => {
                state.loading = false;
                state.successMessage = action.payload.message;
            })
            .addCase(logoutUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || "Logout failed";
            })

            // Logout all devices
            .addCase(logoutAllDevices.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.successMessage = null;
            })
            .addCase(logoutAllDevices.fulfilled, (state, action: PayloadAction<LogoutResponse>) => {
                state.loading = false;
                state.successMessage = action.payload.message;
            })
            .addCase(logoutAllDevices.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || "Logout all devices failed";
            });
    },
});

// ---------------------------- Exports ----------------------------
// Export reducer actions (e.g., clearLogoutState)
export const { clearLogoutState } = logoutSlice.actions;

// Export the slice reducer to add into the store
export default logoutSlice.reducer;
