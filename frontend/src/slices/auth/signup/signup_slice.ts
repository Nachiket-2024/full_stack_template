// ---------------------------- External Imports ----------------------------

// Import createSlice and createAsyncThunk from Redux Toolkit to create state slices and async actions
import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";

// Axios for making HTTP requests
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------

// Import types for signup request/response payloads
import type { SignupRequest, SignupResponse } from "@/slices/auth/signup/signup_types";

// Import centralized settings
import { settings } from "@/core/settings";

// ---------------------------- Async Thunks ----------------------------

// Define an async thunk for handling signup requests
export const signup = createAsyncThunk<
    SignupResponse,          // The type of the resolved value on success
    SignupRequest,           // The type of the argument passed to the thunk
    { rejectValue: string }  // The type of the error if rejected
>(
    "auth/signup",           // Action type prefix
    async (payload, thunkAPI) => {
        try {
            // Send POST request to backend /auth/signup
            const response = await axios.post<SignupResponse>(
                `${settings.apiBaseUrl}/auth/signup`,  // Loaded from settings, no hardcoding
                payload
            );

            // Return the response data on success
            return response.data;
        } catch (error: any) {
            // Extract error message (fallback to "Signup failed")
            const message = error.response?.data?.error || "Signup failed";
            // Reject with error message
            return thunkAPI.rejectWithValue(message);
        }
    }
);

// ---------------------------- Slice State ----------------------------

// Define the shape of the signup slice state
interface SignupState {
    loading: boolean;          // Tracks whether signup is in progress
    error: string | null;      // Holds error message if signup fails
    success: boolean;          // Indicates if signup succeeded
}

// Initial state for signup slice
const initialState: SignupState = {
    loading: false,
    error: null,
    success: false,
};

// ---------------------------- Slice ----------------------------

// Create signup slice
const signupSlice = createSlice({
    name: "signup",            // Slice name (used as prefix for actions)
    initialState,              // Initial state
    reducers: {
        // Reset state back to initial (useful after navigating away from signup page)
        resetSignupState: (state) => {
            state.loading = false;
            state.error = null;
            state.success = false;
        },
    },
    extraReducers: (builder) => {
        // Handle pending state when signup request is triggered
        builder.addCase(signup.pending, (state) => {
            state.loading = true;
            state.error = null;
            state.success = false;
        });

        // Handle fulfilled state when signup succeeds
        builder.addCase(signup.fulfilled, (state) => {
            state.loading = false;
            state.success = true;
        });

        // Handle rejected state when signup fails
        builder.addCase(signup.rejected, (state, action: PayloadAction<any>) => {
            state.loading = false;
            state.error = action.payload || "Signup failed";
        });
    },
});

// ---------------------------- Exports ----------------------------

// Export actions from slice (e.g., resetSignupState)
export const { resetSignupState } = signupSlice.actions;

// Export reducer to be included in the store
export default signupSlice.reducer;
