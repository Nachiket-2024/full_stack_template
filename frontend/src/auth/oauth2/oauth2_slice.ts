// ---------------------------- External Imports ----------------------------
// Import createSlice and type PayloadAction from Redux Toolkit
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- State Type ----------------------------
// Define Redux state structure for OAuth2 authentication
interface OAuth2State {
    loading: boolean;          // Step 1: True if login or token verification is in progress
    error: string | null;      // Step 2: Stores error message if login fails
    isAuthenticated: boolean;  // Step 3: True if user is authenticated (valid session/cookie)
    user: {                     // Step 4: Basic user information from backend
        id: string;
        email: string;
        role: string;
    } | null;
}

// ---------------------------- Initial State ----------------------------
const initialState: OAuth2State = {
    loading: false,          // Step 1
    error: null,             // Step 2
    isAuthenticated: false,  // Step 3
    user: null,              // Step 4
};

// ---------------------------- Slice ----------------------------
/**
 * oauth2Slice
 * Manages OAuth2 login/session state
 * Methods:
 *   1. setUserSession - Store user session after successful login
 *   2. clearUserSession - Clear session (logout or invalid token)
 *   3. setOAuth2Error - Set error message and reset session
 *   4. setOAuth2Loading - Set loading true while waiting for redirect/callback
 */
const oauth2Slice = createSlice({
    name: "oauth2",       // Step 1: Slice name
    initialState,         // Step 2: Initial state
    reducers: {
        /**
         * setUserSession
         * Input: User object {id, email, role}
         * Process:
         *   1. Stop loading
         *   2. Clear previous error
         *   3. Mark user as authenticated
         *   4. Store user info
         * Output: Redux state updated with authenticated user
         */
        setUserSession: (
            state,
            action: PayloadAction<{ id: string; email: string; role: string }>
        ) => {
            state.loading = false;        // Step 1
            state.error = null;           // Step 2
            state.isAuthenticated = true; // Step 3
            state.user = action.payload;  // Step 4
        },

        /**
         * clearUserSession
         * Input: None
         * Process:
         *   1. Stop loading
         *   2. Clear error
         *   3. Mark as not authenticated
         *   4. Remove user info
         * Output: Redux state reset to initial unauthenticated values
         */
        clearUserSession: (state) => {
            state.loading = false;         // Step 1
            state.error = null;            // Step 2
            state.isAuthenticated = false; // Step 3
            state.user = null;             // Step 4
        },

        /**
         * setOAuth2Error
         * Input: Error message string
         * Process:
         *   1. Stop loading
         *   2. Store error message
         *   3. Mark as not authenticated
         *   4. Remove user info
         * Output: Redux state updated with error
         */
        setOAuth2Error: (state, action: PayloadAction<string>) => {
            state.loading = false;         // Step 1
            state.error = action.payload;  // Step 2
            state.isAuthenticated = false; // Step 3
            state.user = null;             // Step 4
        },

        /**
         * setOAuth2Loading
         * Input: None
         * Process:
         *   1. Mark loading true
         *   2. Clear previous error
         * Output: Redux state shows loading in progress
         */
        setOAuth2Loading: (state) => {
            state.loading = true;          // Step 1
            state.error = null;            // Step 2
        },
    },
});

// ---------------------------- Exports ----------------------------
// Export slice actions
export const {
    setUserSession,
    clearUserSession,
    setOAuth2Error,
    setOAuth2Loading,
} = oauth2Slice.actions;

// Export reducer for store integration
export default oauth2Slice.reducer;
