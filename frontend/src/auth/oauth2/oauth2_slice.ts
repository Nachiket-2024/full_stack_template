// ---------------------------- External Imports ----------------------------
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------
import type { OAuth2LoginPayload, OAuth2LoginResponse } from "./oauth2_types";

// ---------------------------- State Type ----------------------------
interface OAuth2State {
    loading: boolean;          // Is the OAuth2 request in progress
    error: string | null;      // Error message if login fails
    accessToken: string | null;
    refreshToken: string | null;
}

// ---------------------------- Initial State ----------------------------
const initialState: OAuth2State = {
    loading: false,
    error: null,
    accessToken: null,
    refreshToken: null,
};

// ---------------------------- Async Thunk ----------------------------
export const oauth2Login = createAsyncThunk<
    OAuth2LoginResponse,   // Success return type
    OAuth2LoginPayload,    // Input argument type
    { rejectValue: string } // Rejected type
>(
    "auth/oauth2Login",
    async (payload: OAuth2LoginPayload, thunkAPI) => {
        try {
            // Backend endpoint to initiate OAuth2 login
            const response = await axios.get<OAuth2LoginResponse>(
                `http://localhost:8000/auth/oauth2/login/${payload.provider}`
            );
            return response.data;
        } catch (error: any) {
            return thunkAPI.rejectWithValue(error.response?.data?.error || "OAuth2 login failed");
        }
    }
);

// ---------------------------- Slice ----------------------------
const oauth2Slice = createSlice({
    name: "oauth2",
    initialState,
    reducers: {
        // Manually clear OAuth2 state
        clearOAuth2State: (state) => {
            state.loading = false;
            state.error = null;
            state.accessToken = null;
            state.refreshToken = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(oauth2Login.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(
                oauth2Login.fulfilled,
                (state, action: PayloadAction<OAuth2LoginResponse>) => {
                    state.loading = false;
                    state.accessToken = action.payload.access_token;
                    state.refreshToken = action.payload.refresh_token;
                }
            )
            .addCase(oauth2Login.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || "OAuth2 login failed";
            });
    },
});

// ---------------------------- Exports ----------------------------
export const { clearOAuth2State } = oauth2Slice.actions;
export default oauth2Slice.reducer;
