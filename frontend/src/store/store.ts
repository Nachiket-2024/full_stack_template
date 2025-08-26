// ---------------------------- External Imports ----------------------------
// Import configureStore to create the Redux store
import { configureStore } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Import login slice reducer (we’ll manage login state here)
import loginReducer from "@/slices/auth_slices/login_slice";

// ---------------------------- Store Setup ----------------------------
// Create the Redux store using Redux Toolkit
export const store = configureStore({
    // Register reducers (each key is a slice of the state tree)
    reducer: {
        // 'login' slice handles authentication (tokens, loading, errors)
        login: loginReducer,
    },
});

// ---------------------------- Types ----------------------------
// RootState represents the full Redux state (useful with useSelector)
export type RootState = ReturnType<typeof store.getState>;

// AppDispatch is the typed dispatch function (useful with useDispatch)
export type AppDispatch = typeof store.dispatch;
