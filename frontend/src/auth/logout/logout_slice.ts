// ---------------------------- External Imports ----------------------------
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------
import type { LogoutPayload, LogoutResponse } from "./logout_types";

// ---------------------------- State Type ----------------------------
interface LogoutState {
    loading: boolean;          // Is logout request in progress
    error: string | null;      // Error message if request fails
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
        const response = await axios.post<LogoutResponse>(
            "http://localhost:8000/auth/logout",
            payload
        );
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
        const response = await axios.post<LogoutResponse>(
            "http://localhost:8000/auth/logout/all",
            payload
        );
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
export const { clearLogoutState } = logoutSlice.actions;
export default logoutSlice.reducer;
