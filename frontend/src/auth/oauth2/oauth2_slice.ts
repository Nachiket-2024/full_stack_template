// ---------------------------- External Imports ----------------------------
// Import createSlice from Redux Toolkit
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- State Type ----------------------------
interface OAuth2State {
    loading: boolean;       // Is login state in progress
    error: string | null;   // Error message if login fails
    isAuthenticated: boolean; // Whether user is authenticated (cookie present + verified)
    user: {                 // Basic user info from backend
        id: string;
        email: string;
        role: string;
    } | null;
}

// ---------------------------- Initial State ----------------------------
const initialState: OAuth2State = {
    loading: false,
    error: null,
    isAuthenticated: false,
    user: null,
};

// ---------------------------- Slice ----------------------------
const oauth2Slice = createSlice({
    name: "oauth2",
    initialState,
    reducers: {
        // Store user session after successful login or token refresh
        setUserSession: (
            state,
            action: PayloadAction<{ id: string; email: string; role: string }>
        ) => {
            state.loading = false;
            state.error = null;
            state.isAuthenticated = true;
            state.user = action.payload;
        },

        // Clear session (logout or invalid cookies)
        clearUserSession: (state) => {
            state.loading = false;
            state.error = null;
            state.isAuthenticated = false;
            state.user = null;
        },

        // Set an OAuth2-related error
        setOAuth2Error: (state, action: PayloadAction<string>) => {
            state.loading = false;
            state.error = action.payload;
            state.isAuthenticated = false;
            state.user = null;
        },

        // Optional: set loading true when waiting for redirect/callback
        setOAuth2Loading: (state) => {
            state.loading = true;
            state.error = null;
        },
    },
});

// ---------------------------- Exports ----------------------------
export const {
    setUserSession,
    clearUserSession,
    setOAuth2Error,
    setOAuth2Loading,
} = oauth2Slice.actions;

export default oauth2Slice.reducer;
