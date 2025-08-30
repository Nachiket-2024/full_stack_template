// ---------------------------- External Imports ----------------------------
// Redux Toolkit functions for slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Type-only import for PayloadAction (required with verbatimModuleSyntax)
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Use signupApi wrapper from auth_api.ts
import { signupApi } from "../../api/auth_api";

// Import types for signup request/response
import type { SignupRequest, SignupResponse } from "./signup_types";

// ---------------------------- State Type ----------------------------
// Redux state for signup
interface SignupState {
    loading: boolean;              // Indicates request in progress
    error: string | null;          // Error message if signup fails
    successMessage: string | null; // Message on successful signup
}

// ---------------------------- Initial State ----------------------------
const initialState: SignupState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunk ----------------------------
// Handles calling the backend signup endpoint via signupApi
export const signupUser = createAsyncThunk<
    SignupResponse,        // Success return type
    SignupRequest,         // Input argument type
    { rejectValue: string } // Error type
>(
    "auth/signup",
    async (payload: SignupRequest, thunkAPI) => {
        try {
            const response = await signupApi(payload);
            return response.data;
        } catch (error: any) {
            // Extract backend error message or fallback
            return thunkAPI.rejectWithValue(error.response?.data?.error || "Signup failed");
        }
    }
);

// ---------------------------- Slice ----------------------------
const signupSlice = createSlice({
    name: "signup",
    initialState,
    reducers: {
        // Reset signup state manually
        clearSignupState: (state) => {
            state.loading = false;
            state.error = null;
            state.successMessage = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(signupUser.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.successMessage = null;
            })
            .addCase(
                signupUser.fulfilled,
                (state, action: PayloadAction<SignupResponse>) => {
                    state.loading = false;
                    state.successMessage = action.payload.message;
                }
            )
            .addCase(signupUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || "Signup failed";
            });
    },
});

// ---------------------------- Exports ----------------------------
export const { clearSignupState } = signupSlice.actions;
export default signupSlice.reducer;
