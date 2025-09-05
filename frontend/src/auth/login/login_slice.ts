// ---------------------------- External Imports ----------------------------
// Import createSlice and createAsyncThunk for Redux logic
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Import type-only PayloadAction for Redux state typing
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Import API functions instead of calling axios directly
import { loginApi, getCurrentUserApi } from "../../api/auth_api";

// Import type-only API request/response types for login
import type { LoginRequest } from "./login_types";

// ---------------------------- State Type ----------------------------
// Redux state specific to login (UI + user), not backend API schema
interface LoginState {
    loading: boolean;          // true when API request is in progress
    error: string | null;      // error message if login fails
    user: { id: string; email: string } | null; // authenticated user info
    isAuthenticated: boolean;  // true if user logged in
}

// ---------------------------- Initial State ----------------------------
const initialState: LoginState = {
    loading: false,
    error: null,
    user: null,
    isAuthenticated: false,
};

// ---------------------------- Async Thunks ----------------------------
// Async function to handle login API call
export const loginUser = createAsyncThunk<
    { id: string; email: string }, // Return type on success
    LoginRequest,                  // Payload type when dispatched
    { rejectValue: string }        // Error type if rejected
>(
    "auth/login",                  // Redux action type
    async (payload: LoginRequest, thunkAPI) => {
        try {
            // 1. Call login API (sets cookies in response)
            await loginApi(payload);
            // 2. Fetch user info using session cookies
            const response = await getCurrentUserApi();
            // 3. Return user data
            return response.data;
        } catch (error: any) {
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Login failed"
            );
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
            state.user = null;
            state.isAuthenticated = false;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(loginUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(
                loginUser.fulfilled,
                (state, action: PayloadAction<{ id: string; email: string }>) => {
                    state.loading = false;
                    state.user = action.payload;
                    state.isAuthenticated = true;
                }
            )
            .addCase(loginUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || "Login failed";
            });
    },
});

// ---------------------------- Exports ----------------------------
export const { clearLoginState } = loginSlice.actions;
export default loginSlice.reducer;
