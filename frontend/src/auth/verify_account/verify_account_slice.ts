// ---------------------------- External Imports ----------------------------
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------
import type { VerifyAccountPayload, VerifyAccountResponse } from "./verify_account_types";

// ---------------------------- State Type ----------------------------
interface VerifyAccountState {
    loading: boolean;          // Is verification request in progress
    error: string | null;      // Error message if verification fails
    successMessage: string | null; // Message on successful verification
}

// ---------------------------- Initial State ----------------------------
const initialState: VerifyAccountState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunk ----------------------------
export const verifyAccount = createAsyncThunk<
    VerifyAccountResponse,  // Success return type
    VerifyAccountPayload,   // Input argument type
    { rejectValue: string } // Rejected type
>("auth/verifyAccount", async (payload, thunkAPI) => {
    try {
        const response = await axios.get<VerifyAccountResponse>(
            `http://localhost:8000/auth/verify-account?token=${payload.token}&email=${payload.email}`
        );
        return response.data;
    } catch (error: any) {
        return thunkAPI.rejectWithValue(error.response?.data?.error || "Account verification failed");
    }
});

// ---------------------------- Slice ----------------------------
const verifyAccountSlice = createSlice({
    name: "verifyAccount",
    initialState,
    reducers: {
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
            .addCase(verifyAccount.fulfilled, (state, action: PayloadAction<VerifyAccountResponse>) => {
                state.loading = false;
                state.successMessage = action.payload.message;
            })
            .addCase(verifyAccount.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || "Account verification failed";
            });
    },
});

// ---------------------------- Exports ----------------------------
export const { clearVerifyAccountState } = verifyAccountSlice.actions;
export default verifyAccountSlice.reducer;
