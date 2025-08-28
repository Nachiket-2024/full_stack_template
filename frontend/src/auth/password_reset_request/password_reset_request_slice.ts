// ---------------------------- External Imports ----------------------------
// Redux Toolkit functions for slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Type-only import for PayloadAction
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Use the API wrapper from auth_api.ts
import { passwordResetRequestApi } from "@/api/auth_api";

// Import types for password reset request
import type {
    PasswordResetRequestPayload,
    PasswordResetRequestResponse,
} from "./password_reset_request_types";

// ---------------------------- State Type ----------------------------
interface PasswordResetRequestState {
    loading: boolean;              // Is the request in progress
    error: string | null;          // Error message if request fails
    successMessage: string | null; // Success message from backend
}

// ---------------------------- Initial State ----------------------------
const initialState: PasswordResetRequestState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunk ----------------------------
// Calls the passwordResetRequestApi from auth_api.ts
export const requestPasswordReset = createAsyncThunk<
    PasswordResetRequestResponse,   // Success return type
    PasswordResetRequestPayload,    // Input argument type
    { rejectValue: string }         // Error type
>(
    "auth/passwordResetRequest",
    async (payload, thunkAPI) => {
        try {
            const response = await passwordResetRequestApi(payload);
            return response.data;
        } catch (error: any) {
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Password reset request failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
const passwordResetRequestSlice = createSlice({
    name: "passwordResetRequest",
    initialState,
    reducers: {
        // Reset state manually
        clearPasswordResetRequestState: (state) => {
            state.loading = false;
            state.error = null;
            state.successMessage = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(requestPasswordReset.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.successMessage = null;
            })
            .addCase(
                requestPasswordReset.fulfilled,
                (state, action: PayloadAction<PasswordResetRequestResponse>) => {
                    state.loading = false;
                    state.successMessage = action.payload.message;
                }
            )
            .addCase(requestPasswordReset.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || "Password reset request failed";
            });
    },
});

// ---------------------------- Exports ----------------------------
export const { clearPasswordResetRequestState } =
    passwordResetRequestSlice.actions;
export default passwordResetRequestSlice.reducer;
