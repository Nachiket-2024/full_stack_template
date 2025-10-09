// ---------------------------- External Imports ----------------------------
// Import Redux Toolkit helpers for creating slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Import type-only PayloadAction for strong typing of actions
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Import API functions for login and fetching current user
import { loginApi, getCurrentUserApi } from "../../api/auth_api";

// Import type-only request type for login payload
import type { LoginRequest } from "./login_types";

// ---------------------------- State Type ----------------------------
// TypeScript interface for Redux login slice state
interface LoginState {
    loading: boolean;          // Step 1: True when API request is in progress
    error: string | null;      // Step 2: Error message if login fails
    user: { id: string; email: string } | null; // Step 3: Authenticated user info
    isAuthenticated: boolean;  // Step 4: True if user is logged in
}

// ---------------------------- Initial State ----------------------------
// Initial state for login slice
const initialState: LoginState = {
    loading: false,            // Step 1
    error: null,               // Step 2
    user: null,                // Step 3
    isAuthenticated: false,    // Step 4
};

// ---------------------------- Async Thunks ----------------------------
/**
 * loginUser
 * Input: LoginRequest payload containing credentials
 * Process:
 *   1. Call login API to authenticate user and set session cookies
 *   2. Fetch current user data using session cookies
 *   3. Return user data if successful
 *   4. Catch errors and reject with meaningful error message
 * Output: Authenticated user data { id, email } or rejected string
 */
export const loginUser = createAsyncThunk<
    { id: string; email: string }, // Return type: user data
    LoginRequest,                  // Payload type: login request
    { rejectValue: string }        // Rejection type: error string
>(
    "auth/login",                  // Action type
    async (payload: LoginRequest, thunkAPI) => {
        try {
            // Step 1: Call login API (sets cookies)
            await loginApi(payload);

            // Step 2: Fetch current user using session cookies
            const response = await getCurrentUserApi("loginUserThunk");

            // Step 3: Return user data on success
            return response.data;
        } catch (error: any) {
            // Step 4: Reject with meaningful error message
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Login failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
/**
 * loginSlice
 * Manages login/authentication state
 * Methods:
 *   1. clearLoginState - Reset login slice to initial state
 */
const loginSlice = createSlice({
    name: "login",       // Step 1: Slice name
    initialState,        // Step 2: Initial state
    reducers: {
        /**
         * clearLoginState
         * Input: None
         * Process:
         *   1. Reset loading to false
         *   2. Clear error
         *   3. Clear user info
         *   4. Set isAuthenticated to false
         * Output: Redux login state reset
         */
        clearLoginState: (state) => {
            state.loading = false;          // Step 1
            state.error = null;             // Step 2
            state.user = null;              // Step 3
            state.isAuthenticated = false;  // Step 4
        },
    },
    extraReducers: (builder) => {
        // Handle async thunk states
        builder
            // Step 1: Pending - loading true, clear error
            .addCase(loginUser.pending, (state) => {
                state.loading = true;        // Step 1a
                state.error = null;          // Step 1b
            })
            // Step 2: Fulfilled - set user info, mark as authenticated
            .addCase(
                loginUser.fulfilled,
                (state, action: PayloadAction<{ id: string; email: string }>) => {
                    state.loading = false;               // Step 2a
                    state.user = action.payload;         // Step 2b
                    state.isAuthenticated = true;        // Step 2c
                }
            )
            // Step 3: Rejected - loading false, store error message
            .addCase(loginUser.rejected, (state, action) => {
                state.loading = false;                 // Step 3a
                state.error = action.payload || "Login failed"; // Step 3b
            });
    },
});

// ---------------------------- Exports ----------------------------
// Export clearLoginState action
export const { clearLoginState } = loginSlice.actions;

// Export reducer for store configuration
export default loginSlice.reducer;
