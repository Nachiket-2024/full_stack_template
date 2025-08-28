// ---------------------------- External Imports ----------------------------
// Redux Toolkit functions for slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Type-only import for PayloadAction
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Use verifyAccountApi wrapper from auth_api.ts
import { verifyAccountApi } from "@/api/auth_api";

// Import types for verify account request/response
import type { VerifyAccountPayload, VerifyAccountResponse } from "./verify_account_types";

// ---------------------------- State Type ----------------------------
// Redux state for account verification
interface VerifyAccountState {
    loading: boolean;              // Indicates request in progress
    error: string | null;          // Error message if verification fails
    successMessage: string | null; // Message on successful verification
}

// ---------------------------- Initial State ----------------------------
const initialState: VerifyAccountState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunk ----------------------------
// Handles calling the backend verify-account endpoint via verifyAccountApi
export const verifyAccount = createAsyncThunk<
    VerifyAccountResponse,   // Success return type
    VerifyAccountPayload,    // Input argument type
    { rejectValue: string }  // Error type
>(
    "auth/verifyAccount",
    async (payload, thunkAPI) => {
        try {
            const response = await verifyAccountApi(payload.token, payload.email);
            return response.data;
        } catch (error: any) {
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Account verification failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
const verifyAccountSlice = createSlice({
    name: "verifyAccount",
    initialState,
    reducers: {
        // Manually clear verification state
        clearVerifyAccountState: (state) => {
            state.loading = false;
            state.error = null;
            state.successMessage = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(verifyAccount.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.successMessage = null;
            })
            .addCase(
                verifyAccount.fulfilled,
                (state, action: PayloadAction<VerifyAccountResponse>) => {
                    state.loading = false;
                    state.successMessage = action.payload.message;
                }
            )
            .addCase(verifyAccount.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || "Account verification failed";
            });
    },
});

// ---------------------------- Exports ----------------------------
export const { clearVerifyAccountState } = verifyAccountSlice.actions;
export default verifyAccountSlice.reducer;
