// ---------------------------- External Imports ----------------------------
// Import createSlice to define Redux slice and PayloadAction for typing actions
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

// Import async thunk to fetch current user info
import { fetchCurrentUser } from "../current_user/current_user_slice";

// ---------------------------- State Type ----------------------------
/**
 * OAuth2State
 * Defines the Redux state shape for OAuth2 login/session:
 * 1. loading: true if login or session verification is in progress
 * 2. error: stores error message string or null
 * 3. isAuthenticated: true if user is logged in
 * 4. user: object containing id, email, and role of user, or null
 */
interface OAuth2State {
    loading: boolean;                                         // Step 1: loading flag
    error: string | null;                                     // Step 2: error message
    isAuthenticated: boolean;                                 // Step 3: authentication status
    user: { id: string; email: string; role: string } | null; // Step 4: user info
}

// ---------------------------- Initial State ----------------------------
/**
 * initialState
 * Default OAuth2 slice state
 */
const initialState: OAuth2State = {
    loading: false,       // Not loading initially
    error: null,          // No error initially
    isAuthenticated: false, // Not authenticated initially
    user: null,           // No user data initially
};

// ---------------------------- Slice ----------------------------
/**
 * oauth2Slice
 * Redux slice handling OAuth2 login/session state:
 * Methods:
 * 1. setUserSession: store user info and mark authenticated
 * 2. clearUserSession: reset state to unauthenticated
 * 3. setOAuth2Error: store error on failed login attempt
 * 4. setOAuth2Loading: set loading state during API calls
 * Extra reducers handle async fetchCurrentUser thunk
 */
const oauth2Slice = createSlice({
    name: "oauth2",
    initialState,
    reducers: {
        /**
         * setUserSession
         * Input: user object { id, email, role }
         * Process:
         *   1. Set loading to false
         *   2. Clear error
         *   3. Mark user as authenticated
         *   4. Store user info in state
         * Output: updated state
         */
        setUserSession: (state, action: PayloadAction<{ id: string; email: string; role: string }>) => {
            state.loading = false;            // Step 1: stop loading
            state.error = null;               // Step 2: clear error
            state.isAuthenticated = true;     // Step 3: authenticated
            state.user = action.payload;      // Step 4: store user info
        },

        /**
         * clearUserSession
         * Input: none
         * Process:
         *   1. Reset loading, error, authentication, and user data
         * Output: updated state
         */
        clearUserSession: (state) => {
            state.loading = false;           // Step 1: stop loading
            state.error = null;              // Step 2: clear error
            state.isAuthenticated = false;   // Step 3: reset auth
            state.user = null;               // Step 4: clear user info
        },

        /**
         * setOAuth2Error
         * Input: error string
         * Process:
         *   1. Stop loading
         *   2. Set error
         *   3. Mark as unauthenticated
         *   4. Clear user data
         * Output: updated state
         */
        setOAuth2Error: (state, action: PayloadAction<string>) => {
            state.loading = false;           // Step 1: stop loading
            state.error = action.payload;    // Step 2: store error
            state.isAuthenticated = false;   // Step 3: reset auth
            state.user = null;               // Step 4: clear user
        },

        /**
         * setOAuth2Loading
         * Input: none
         * Process:
         *   1. Set loading to true
         *   2. Clear error
         * Output: updated state
         */
        setOAuth2Loading: (state) => {
            state.loading = true;            // Step 1: start loading
            state.error = null;              // Step 2: clear error
        },
    },
    extraReducers: (builder) => {
        /**
         * Handle fetchCurrentUser async thunk
         * 1. pending: set loading true
         * 2. fulfilled: update authentication state
         * 3. rejected: set unauthenticated, but do not set error
         */
        builder.addCase(fetchCurrentUser.pending, (state) => {
            state.loading = true;           // Step 1: set loading
            state.error = null;             // Step 1: clear error
        });

        builder.addCase(fetchCurrentUser.fulfilled, (state, action: PayloadAction<boolean>) => {
            state.loading = false;          // Step 2: stop loading
            state.isAuthenticated = action.payload; // Step 2: set auth status
        });

        builder.addCase(fetchCurrentUser.rejected, (state) => {
            state.loading = false;          // Step 3: stop loading
            state.isAuthenticated = false;  // Step 3: unauthenticated
            // Step 3: do NOT set error
        });
    },
});

// ---------------------------- Exports ----------------------------
// Export slice actions for dispatch
export const { setUserSession, clearUserSession, setOAuth2Error, setOAuth2Loading } = oauth2Slice.actions;

// Export reducer as default
export default oauth2Slice.reducer;