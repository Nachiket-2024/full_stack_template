// ---------------------------- External Imports ----------------------------
// Redux Toolkit functions for slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Type-only import for PayloadAction
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Use the API wrapper from auth_api.ts
import { passwordResetConfirmApi } from "@/api/auth_api";

// Import types for password reset confirmation
import type {
    PasswordResetConfirmPayload,
    PasswordResetConfirmResponse,
} from "./password_reset_confirm_types";

// ---------------------------- State Type ----------------------------
interface PasswordResetConfirmState {
    loading: boolean;              // Is the request in progress
    error: string | null;          // Error message if request fails
    successMessage: string | null; // Success message from backend
}

// ---------------------------- Initial State ----------------------------
const initialState: PasswordResetConfirmState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunk ----------------------------
// Calls the passwordResetConfirmApi from auth_api.ts
export const confirmPasswordReset = createAsyncThunk<
    PasswordResetConfirmResponse,   // Success return type
    PasswordResetConfirmPayload,    // Input type
    { rejectValue: string }         // Error type
>(
    "auth/passwordResetConfirm",
    async (payload, thunkAPI) => {
        try {
            const response = await passwordResetConfirmApi(payload);
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
        // Reset state manually
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
