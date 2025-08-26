// ---------------------------- External Imports ----------------------------
// Import createSlice and createAsyncThunk for Redux logic
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Import type-only PayloadAction
import type { PayloadAction } from "@reduxjs/toolkit";

// Import axios instance for API calls
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------
// Import LoginRequest & LoginResponse types (backend contracts)
import type { LoginRequest, LoginResponse } from "@/types/auth_types/login_types";

// ---------------------------- State Type ----------------------------
// State for login slice (Redux-specific, not API schema)
interface LoginState {
    loading: boolean;
    error: string | null;
    accessToken: string | null;
    refreshToken: string | null;
}

// ---------------------------- Initial State ----------------------------
const initialState: LoginState = {
    loading: false,
    error: null,
    accessToken: null,
    refreshToken: null,
};

// ---------------------------- Async Thunk (API Call) ----------------------------
// Handles calling the backend login endpoint
export const loginUser = createAsyncThunk<
    LoginResponse,       // Success return type
    LoginRequest,        // Input argument type
    { rejectValue: string } // Rejected type
>(
    "auth/login",
    async (payload: LoginRequest, thunkAPI) => {
        try {
            const response = await axios.post<LoginResponse>(
                "http://localhost:8000/auth/login",
                payload
            );
            return response.data;
        } catch (error: any) {
            return thunkAPI.rejectWithValue(error.response?.data?.error || "Login failed");
        }
    }
);

// ---------------------------- Slice ----------------------------
const loginSlice = createSlice({
    name: "login",
    initialState,
    reducers: {
        // Clear login state manually
        clearLoginState: (state) => {
            state.loading = false;
            state.error = null;
            state.accessToken = null;
            state.refreshToken = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(loginUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(loginUser.fulfilled, (state, action: PayloadAction<LoginResponse>) => {
                state.loading = false;
                state.accessToken = action.payload.access_token;
                state.refreshToken = action.payload.refresh_token;
            })
            .addCase(loginUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || "Login failed";
            });
    },
});

// ---------------------------- Exports ----------------------------
export const { clearLoginState } = loginSlice.actions;
export default loginSlice.reducer;
