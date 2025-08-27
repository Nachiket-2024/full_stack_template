// ---------------------------- External Imports ----------------------------
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- State Type ----------------------------
interface OAuth2State {
    loading: boolean;          // Is token processing in progress
    error: string | null;      // Error message if login fails
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
        // ---------------------------- Store Tokens from OAuth2 Callback ----------------------------
        storeOAuth2Tokens: (
            state,
            action: PayloadAction<{ accessToken: string; refreshToken: string }>
        ) => {
            state.loading = false;
            state.error = null;
            state.accessToken = action.payload.accessToken;
            state.refreshToken = action.payload.refreshToken;
        },

        // ---------------------------- Clear OAuth2 State ----------------------------
        clearOAuth2State: (state) => {
            state.loading = false;
            state.error = null;
            state.accessToken = null;
            state.refreshToken = null;
        },

        // ---------------------------- Set Error ----------------------------
        setOAuth2Error: (state, action: PayloadAction<string>) => {
            state.loading = false;
            state.error = action.payload;
            state.accessToken = null;
            state.refreshToken = null;
        },
    },
});

// ---------------------------- Exports ----------------------------
export const { storeOAuth2Tokens, clearOAuth2State, setOAuth2Error } = oauth2Slice.actions;
export default oauth2Slice.reducer;
