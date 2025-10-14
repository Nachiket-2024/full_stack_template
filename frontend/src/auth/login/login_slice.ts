// ---------------------------- External Imports ----------------------------
// Import Redux Toolkit functions for creating slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Import PayloadAction type for typed action handling
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Import authentication API functions
import { loginApi, getCurrentUserApi } from "../../api/auth_api";

// Import types for login request payload
import type { LoginRequest } from "./login_types";

// ---------------------------- Async Thunks ----------------------------
// fetchCurrentUser: Fetch current user session and update auth state
/**
 * Input: Optional source string for logging/debugging
 * Process:
 *   1. Call API to fetch current user
 *   2. Return true if API response status is 200 (authenticated)
 *   3. Reject with false on API error
 * Output: boolean indicating authentication status
 */
export const fetchCurrentUser = createAsyncThunk<
    boolean,
    string | undefined,
    { rejectValue: boolean }
>(
    "currentUser/fetchCurrentUser",
    async (src = "ReduxSlice", { rejectWithValue }) => {
        try {
            // Step 1: Call API to get current user
            const res = await getCurrentUserApi(src);

            // Step 2: Return true if API confirms authentication
            return res.status === 200;
        } catch {
            // Step 3: Reject with false on error
            return rejectWithValue(false);
        }
    }
);

// loginUser: Handles login and updates Redux auth state
/**
 * Input: LoginRequest payload
 * Process:
 *   1. Call login API with credentials
 *   2. Update authentication state using fetchCurrentUser
 *   3. Fetch user info if authenticated
 *   4. Return user info or reject with error
 * Output: { id, email } on success, or error string
 */
export const loginUser = createAsyncThunk<
    { id: string; email: string },
    LoginRequest,
    { rejectValue: string }
>(
    "auth/login",
    async (payload, thunkAPI) => {
        try {
            // Step 1: Call login API
            await loginApi(payload);

            // Step 2: Update auth state in Redux
            const isAuth = await thunkAPI.dispatch(fetchCurrentUser("loginUserThunk")).unwrap();
            if (!isAuth) throw new Error("Authentication failed");

            // Step 3: Fetch user info
            const res = await getCurrentUserApi("loginUserThunk");

            // Step 4: Return user info
            return res.data;
        } catch (error: any) {
            // Step 4: Reject with meaningful error message
            return thunkAPI.rejectWithValue(error.response?.data?.error || "Login failed");
        }
    }
);

// ---------------------------- State Type ----------------------------
// Redux state for login/authentication
interface LoginState {
    loading: boolean;                       // Indicates if login or fetch is in progress
    error: string | null;                   // Stores error message if any
    user: { id: string; email: string } | null; // Authenticated user info
    isAuthenticated: boolean;               // Authentication status
}

// ---------------------------- Initial State ----------------------------
// Initialize login slice state
const initialState: LoginState = {
    loading: false,                          // Step 1
    error: null,                             // Step 2
    user: null,                              // Step 3
    isAuthenticated: false,                  // Step 4
};

// ---------------------------- Slice ----------------------------
// loginSlice: Manages login and authentication state
const loginSlice = createSlice({
    name: "login",                            // Step 1: Slice name
    initialState,                             // Step 2: Initial state
    reducers: {
        // clearLoginState: Reset entire slice to initial state
        clearLoginState: (state) => {
            state.loading = false;           // Step 1
            state.error = null;              // Step 2
            state.user = null;               // Step 3
            state.isAuthenticated = false;   // Step 4
        },

        // resetAuthMessages: Clear any stale error messages
        /**
         * Input: None
         * Process:
         *   1. Clear error message
         * Output: Cleared error state
         */
        resetAuthMessages: (state) => {
            state.error = null;               // Step 1
        }
    },
    extraReducers: (builder) => {
        // loginUser pending: mark loading and clear errors
        builder.addCase(loginUser.pending, (state) => {
            state.loading = true;             // Step 1
            state.error = null;               // Step 2
        });

        // loginUser fulfilled: store user info, mark authenticated
        builder.addCase(loginUser.fulfilled, (state, action: PayloadAction<{ id: string; email: string }>) => {
            state.loading = false;             // Step 1
            state.user = action.payload;       // Step 2
            state.isAuthenticated = true;      // Step 3
            state.error = null;                // Step 4: Clear stale messages
        });

        // loginUser rejected: store error and mark unauthenticated
        builder.addCase(loginUser.rejected, (state, action) => {
            state.loading = false;             // Step 1
            state.error = action.payload || "Login failed"; // Step 2
            state.isAuthenticated = false;     // Step 3
        });

        // fetchCurrentUser fulfilled: update auth state
        builder.addCase(fetchCurrentUser.fulfilled, (state, action: PayloadAction<boolean>) => {
            state.isAuthenticated = action.payload; // Step 1
        });

        // fetchCurrentUser rejected: mark unauthenticated
        builder.addCase(fetchCurrentUser.rejected, (state) => {
            state.isAuthenticated = false;     // Step 1
        });
    },
});

// ---------------------------- Exports ----------------------------
// Export actions for slice
export const { clearLoginState, resetAuthMessages } = loginSlice.actions;

// Export reducer for store
export default loginSlice.reducer;
