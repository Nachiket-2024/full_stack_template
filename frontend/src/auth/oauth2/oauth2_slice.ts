// ---------------------------- External Imports ----------------------------
// Import Redux Toolkit functions for creating slices
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

// Import fetchCurrentUser thunk to reuse existing authentication check
import { fetchCurrentUser } from "../current_user/current_user_slice";

// ---------------------------- State Type ----------------------------
// Redux state structure for OAuth2 authentication
interface OAuth2State {
    loading: boolean;                                         // Step 1: True if login/session verification in progress
    error: string | null;                                     // Step 2: Stores error messages
    isAuthenticated: boolean;                                 // Step 3: True if user is authenticated
    user: { id: string; email: string; role: string } | null; // Step 4: Basic user info from backend
}

// ---------------------------- Initial State ----------------------------
const initialState: OAuth2State = {
    loading: false,
    error: null,
    isAuthenticated: false,
    user: null,
};

// ---------------------------- Slice ----------------------------
/**
 * oauth2Slice
 * Manages OAuth2 authentication state
 * 
 * Methods:
 *   1. setUserSession - Store user info and mark authenticated
 *   2. clearUserSession - Clear user info and mark unauthenticated
 *   3. setOAuth2Error - Store error and mark unauthenticated
 *   4. setOAuth2Loading - Set loading state
 */
const oauth2Slice = createSlice({
    name: "oauth2",
    initialState,
    reducers: {
        // setUserSession: Store user info and mark authenticated
        setUserSession: (state, action: PayloadAction<{ id: string; email: string; role: string }>) => {
            state.loading = false;
            state.error = null;
            state.isAuthenticated = true;
            state.user = action.payload;
        },

        // clearUserSession: Reset state to unauthenticated
        clearUserSession: (state) => {
            state.loading = false;
            state.error = null;
            state.isAuthenticated = false;
            state.user = null;
        },

        // setOAuth2Error: Store error and mark unauthenticated
        setOAuth2Error: (state, action: PayloadAction<string>) => {
            state.loading = false;
            state.error = action.payload;
            state.isAuthenticated = false;
            state.user = null;
        },

        // setOAuth2Loading: Set loading state during API calls
        setOAuth2Loading: (state) => {
            state.loading = true;
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        // fetchCurrentUser pending: set loading
        builder.addCase(fetchCurrentUser.pending, (state) => {
            state.loading = true;
            state.error = null;
        });

        // fetchCurrentUser fulfilled: update authentication state
        builder.addCase(fetchCurrentUser.fulfilled, (state, action: PayloadAction<boolean>) => {
            state.loading = false;
            state.isAuthenticated = action.payload;
        });

        // fetchCurrentUser rejected: mark unauthenticated and store error
        builder.addCase(fetchCurrentUser.rejected, (state) => {
            state.loading = false;
            state.isAuthenticated = false;
            state.error = "Failed to fetch current user";
        });
    },
});

// ---------------------------- Exports ----------------------------
// Export actions to manipulate OAuth2 state
export const { setUserSession, clearUserSession, setOAuth2Error, setOAuth2Loading } = oauth2Slice.actions;

// Export reducer for store integration
export default oauth2Slice.reducer;
