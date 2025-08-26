// ---------------------------- External Imports ----------------------------
// Import createSlice and createAsyncThunk for Redux logic
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Import type-only PayloadAction for Redux state typing
import type { PayloadAction } from "@reduxjs/toolkit";

// Import axios for making API requests
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------
// Import type-only API request/response types for login
import type { LoginRequest, LoginResponse } from "./login_types";

// ---------------------------- State Type ----------------------------
// Redux state specific to login (UI + tokens), not backend API schema
interface LoginState {
    loading: boolean;         // true when API request is in progress
    error: string | null;     // error message if login fails
    accessToken: string | null;  // JWT access token
    refreshToken: string | null; // JWT refresh token
}

// ---------------------------- Initial State ----------------------------
const initialState: LoginState = {
    loading: false,
    error: null,
    accessToken: null,
    refreshToken: null,
};

// ---------------------------- Async Thunk ----------------------------
// Async function to handle login API call
export const loginUser = createAsyncThunk<
    LoginResponse,          // Return type on success
    LoginRequest,           // Payload type when dispatched
    { rejectValue: string } // Error type if rejected
>(
    "auth/login",           // Redux action type
    async (payload: LoginRequest, thunkAPI) => {
        try {
            // Make POST request to backend /auth/login
            const response = await axios.post<LoginResponse>(
                "http://localhost:8000/auth/login",
                payload
            );
            // Return successful response data
            return response.data;
        } catch (error: any) {
            // If error occurs, reject with a message
            return thunkAPI.rejectWithValue(error.response?.data?.error || "Login failed");
        }
    }
);

// ---------------------------- Slice ----------------------------
const loginSlice = createSlice({
    name: "login",       // Slice name
    initialState,        // Starting state
    reducers: {
        // Clear the login state (e.g., on logout)
        clearLoginState: (state) => {
            state.loading = false;
            state.error = null;
            state.accessToken = null;
            state.refreshToken = null;
        },
    },
    extraReducers: (builder) => {
        // Handle pending, fulfilled, and rejected states of loginUser thunk
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
// Export reducer actions (e.g., clearLoginState)
export const { clearLoginState } = loginSlice.actions;

// Export the slice reducer to add into the store
export default loginSlice.reducer;
