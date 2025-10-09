// ---------------------------- External Imports ----------------------------
// Import Redux Toolkit helpers for slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Import API function to get current user
import { getCurrentUserApi } from "../../api/auth_api";

// ---------------------------- Async Thunks ----------------------------
/**
 * fetchCurrentUser
 * Input: Optional source string to indicate origin of fetch call
 * Process:
 *   1. Log the source of the fetch call
 *   2. Call API to get current user
 *   3. Return true if API response is successful (status 200)
 *   4. Catch errors and reject with false
 * Output: boolean indicating authentication status; rejected with false on error
 */
export const fetchCurrentUser = createAsyncThunk<
    boolean,            // Return type: boolean if authenticated
    string | undefined, // Argument type: optional source string
    { rejectValue: boolean } // Rejection type
>(
    "currentUser/fetchCurrentUser", // Action type
    async (src: string = "ReduxSlice", { rejectWithValue }) => {
        try {
            // Step 1: Log the source of the fetch call
            console.log("fetchCurrentUser called from:", src);

            // Step 2: Call API to get current user
            const res = await getCurrentUserApi(src);

            // Step 3: Return true if API response is 200
            return res.status === 200;
        } catch (err) {
            // Step 4: Reject with false if error occurs
            return rejectWithValue(false);
        }
    }
);

// ---------------------------- Slice ----------------------------
/**
 * currentUserSlice
 * Manages the current user authentication state
 * Methods:
 *   1. resetAuthState - Reset authentication state to initial values
 */
interface CurrentUserState {
    isAuthenticated: boolean | null; // Step 1: null = not checked yet
    loading: boolean;                // Step 2: Loading indicator
    error: string | null;            // Step 3: Error message
}

// Initial state for slice
const initialState: CurrentUserState = {
    isAuthenticated: null, // Step 1
    loading: false,        // Step 2
    error: null,           // Step 3
};

// Create slice for current user
export const currentUserSlice = createSlice({
    name: "currentUser",  // Step 1: Slice name
    initialState,         // Step 2: Set initial state
    reducers: {
        /**
         * resetAuthState
         * Input: None
         * Process:
         *   1. Reset isAuthenticated to null
         *   2. Reset loading to false
         *   3. Reset error to null
         * Output: Redux state reset
         */
        resetAuthState: (state) => {
            state.isAuthenticated = null; // Step 1
            state.loading = false;        // Step 2
            state.error = null;           // Step 3
        },
    },
    extraReducers: (builder) => {
        // Handle async thunk states
        builder
            // Step 1: Pending state - set loading true, clear error
            .addCase(fetchCurrentUser.pending, (state) => {
                state.loading = true; // Step 1a
                state.error = null;   // Step 1b
            })
            // Step 2: Fulfilled state - set authentication, stop loading
            .addCase(fetchCurrentUser.fulfilled, (state, action) => {
                state.loading = false;               // Step 2a
                state.isAuthenticated = action.payload; // Step 2b
            })
            // Step 3: Rejected state - set auth false, stop loading, set error
            .addCase(fetchCurrentUser.rejected, (state) => {
                state.loading = false;                 // Step 3a
                state.isAuthenticated = false;        // Step 3b
                state.error = "Failed to fetch current user"; // Step 3c
            });
    },
});

// ---------------------------- Export ----------------------------
// Export reset action
export const { resetAuthState } = currentUserSlice.actions;

// Export reducer for store
export default currentUserSlice.reducer;
