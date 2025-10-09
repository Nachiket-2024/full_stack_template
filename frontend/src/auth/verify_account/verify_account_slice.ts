// ---------------------------- External Imports ----------------------------
// Redux Toolkit functions for creating slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Type-only import for PayloadAction
import type { PayloadAction } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// API function to verify account
import { verifyAccountApi } from "../../api/auth_api";

// Types for verify account request and response
import type { VerifyAccountPayload, VerifyAccountResponse } from "./verify_account_types";

// ---------------------------- State Type ----------------------------
// Defines the Redux state structure for account verification
interface VerifyAccountState {
    loading: boolean;              // Indicates request in progress
    error: string | null;          // Error message if verification fails
    successMessage: string | null; // Message on successful verification
}

// ---------------------------- Initial State ----------------------------
// Default state values for account verification
const initialState: VerifyAccountState = {
    loading: false,
    error: null,
    successMessage: null,
};

// ---------------------------- Async Thunk ----------------------------
// Async action to verify the account using the backend API
// Methods:
// 1. verifyAccount - Calls API to verify account and handles success/error
export const verifyAccount = createAsyncThunk<
    VerifyAccountResponse,   // Success return type
    VerifyAccountPayload,    // Input argument type
    { rejectValue: string }  // Error type
>(
    "auth/verifyAccount",
    async (payload, thunkAPI) => {
        /**
         * Input:
         *   1. payload: VerifyAccountPayload containing email and token
         * Process:
         *   1. Call verifyAccountApi with token and email
         *   2. Return response data if successful
         *   3. Catch errors and reject with meaningful message
         * Output:
         *   1. VerifyAccountResponse if successful
         *   2. Reject with string message if error occurs
         */
        try {
            // Step 1: Call the API with token and email from payload
            const response = await verifyAccountApi(payload.token, payload.email);

            // Step 2: Return the successful response data
            return response.data;
        } catch (error: any) {
            // Step 3: Reject with error message if API call fails
            return thunkAPI.rejectWithValue(
                error.response?.data?.error || "Account verification failed"
            );
        }
    }
);

// ---------------------------- Slice ----------------------------
// Redux slice managing verify account state
// Methods:
// 1. clearVerifyAccountState - Resets the verification state
// 2. Extra reducers for verifyAccount async thunk
const verifyAccountSlice = createSlice({
    name: "verifyAccount",
    initialState,
    reducers: {
        // ---------------------------- Clear State ----------------------------
        clearVerifyAccountState: (state) => {
            /**
             * Input: None
             * Process:
             *   1. Set loading to false
             *   2. Clear error
             *   3. Clear success message
             * Output: State reset to initial values
             */
            state.loading = false;         // Step 1
            state.error = null;            // Step 2
            state.successMessage = null;   // Step 3
        },
    },
    extraReducers: (builder) => {
        builder
            // ---------------------------- Pending ----------------------------
            .addCase(verifyAccount.pending, (state) => {
                /**
                 * Input: None
                 * Process:
                 *   1. Set loading flag
                 *   2. Clear error
                 *   3. Clear success message
                 * Output: State reflects pending API request
                 */
                state.loading = true;        // Step 1
                state.error = null;          // Step 2
                state.successMessage = null; // Step 3
            })
            // ---------------------------- Fulfilled ----------------------------
            .addCase(
                verifyAccount.fulfilled,
                (state, action: PayloadAction<VerifyAccountResponse>) => {
                    /**
                     * Input: action.payload of type VerifyAccountResponse
                     * Process:
                     *   1. Set loading to false
                     *   2. Store success message from payload
                     * Output: State reflects successful verification
                     */
                    state.loading = false;                 // Step 1
                    state.successMessage = action.payload.message; // Step 2
                }
            )
            // ---------------------------- Rejected ----------------------------
            .addCase(verifyAccount.rejected, (state, action) => {
                /**
                 * Input: action.payload containing error message
                 * Process:
                 *   1. Set loading to false
                 *   2. Store error message or default
                 * Output: State reflects failed verification
                 */
                state.loading = false;                           // Step 1
                state.error = action.payload || "Account verification failed"; // Step 2
            });
    },
});

// ---------------------------- Exports ----------------------------
// Export action to manually clear verification state
export const { clearVerifyAccountState } = verifyAccountSlice.actions;

// Export the reducer for integration into the store
export default verifyAccountSlice.reducer;
