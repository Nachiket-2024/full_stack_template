// ---------------------------- External Imports ----------------------------
// Redux Toolkit functions for slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Type-only import for PayloadAction
import type { PayloadAction } from "@reduxjs/toolkit";

// Axios for API calls
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------
// Import types for password reset request
import type {
    PasswordResetRequestPayload,
    PasswordResetRequestResponse,
} from "./password_reset_request_types";

// ---------------------------- State Type ----------------------------
interface PasswordResetRequestState {
    loading: boolean;       // Indicates if the request is in progress
    error: string | null;   // Error message if request fails
    successMessage: string | null; // Message on successful request
}

// ---------------------------- Initial State ----------------------------
const initialState: PasswordResetRequestState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunk ----------------------------
// Handles calling the backend password-reset/request endpoint
export const requestPasswordReset = createAsyncThunk<
    PasswordResetRequestResponse,           // Success return type
    PasswordResetRequestPayload,            // Input argument type
    { rejectValue: string }                 // Rejected type
>(
    "auth/passwordResetRequest",
    async (payload: PasswordResetRequestPayload, thunkAPI) => {
        try {
            const response = await axios.post<PasswordResetRequestResponse>(
                "http://localhost:8000/auth/password-reset/request",
                payload
            );
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
        // Clear the slice state manually
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
