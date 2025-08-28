// ---------------------------- External Imports ----------------------------
// Import createSlice from Redux Toolkit
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- State Type ----------------------------
interface OAuth2State {
    loading: boolean;            // Is login state in progress
    error: string | null;        // Error message if login fails
    accessToken: string | null;  // Access token from backend
    refreshToken: string | null; // Refresh token from backend
}

// ---------------------------- Initial State ----------------------------
const initialState: OAuth2State = {
    loading: false,
    error: null,
    accessToken: null,
    refreshToken: null,
};

// ---------------------------- Slice ----------------------------
const oauth2Slice = createSlice({
    name: "oauth2",
    initialState,
    reducers: {
        // Store tokens from backend after redirect/callback
        storeOAuth2Tokens: (
            state,
            action: PayloadAction<{ accessToken: string; refreshToken: string }>
        ) => {
            state.loading = false;
            state.error = null;
            state.accessToken = action.payload.accessToken;
            state.refreshToken = action.payload.refreshToken;
        },

        // Clear tokens + reset state
        clearOAuth2State: (state) => {
            state.loading = false;
            state.error = null;
            state.accessToken = null;
            state.refreshToken = null;
        },

        // Set an OAuth2-related error
        setOAuth2Error: (state, action: PayloadAction<string>) => {
            state.loading = false;
            state.error = action.payload;
            state.accessToken = null;
            state.refreshToken = null;
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
    storeOAuth2Tokens,
    clearOAuth2State,
    setOAuth2Error,
    setOAuth2Loading,
} = oauth2Slice.actions;

export default oauth2Slice.reducer;
