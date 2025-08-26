// ---------------------------- External Imports ----------------------------
// Redux Toolkit functions for slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Type-only import for PayloadAction
import type { PayloadAction } from "@reduxjs/toolkit";

// Axios for API calls
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------
// Import types for password reset confirmation
import type {
    PasswordResetConfirmPayload,
    PasswordResetConfirmResponse,
} from "./password_reset_confirm_types";

// ---------------------------- State Type ----------------------------
interface PasswordResetConfirmState {
    loading: boolean;       // Indicates if the request is in progress
    error: string | null;   // Error message if request fails
    successMessage: string | null; // Message on successful password reset
}

// ---------------------------- Initial State ----------------------------
const initialState: PasswordResetConfirmState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunk ----------------------------
// Handles calling the backend password-reset/confirm endpoint
export const confirmPasswordReset = createAsyncThunk<
    PasswordResetConfirmResponse,           // Success return type
    PasswordResetConfirmPayload,            // Input argument type
    { rejectValue: string }                 // Rejected type
>(
    "auth/passwordResetConfirm",
    async (payload: PasswordResetConfirmPayload, thunkAPI) => {
        try {
            const response = await axios.post<PasswordResetConfirmResponse>(
                "http://localhost:8000/auth/password-reset/confirm",
                payload
            );
            return response.data;
        } catch (error: any) {
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Password reset confirmation failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
const passwordResetConfirmSlice = createSlice({
    name: "passwordResetConfirm",
    initialState,
    reducers: {
        // Clear the slice state manually
        clearPasswordResetConfirmState: (state) => {
            state.loading = false;
            state.error = null;
            state.successMessage = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(confirmPasswordReset.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.successMessage = null;
            })
            .addCase(
                confirmPasswordReset.fulfilled,
                (state, action: PayloadAction<PasswordResetConfirmResponse>) => {
                    state.loading = false;
                    state.successMessage = action.payload.message;
                }
            )
            .addCase(confirmPasswordReset.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || "Password reset confirmation failed";
            });
    },
});

// ---------------------------- Exports ----------------------------
export const { clearPasswordResetConfirmState } =
    passwordResetConfirmSlice.actions;
export default passwordResetConfirmSlice.reducer;
