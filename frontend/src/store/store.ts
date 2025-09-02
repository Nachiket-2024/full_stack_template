// ---------------------------- External Imports ----------------------------
// Import configureStore from Redux Toolkit to create the Redux store
import { configureStore } from "@reduxjs/toolkit";

// ---------------------------- Internal Imports ----------------------------
// Import reducers for authentication-related slices
import loginReducer from "../auth/login/login_slice";
import signupReducer from "../auth/signup/signup_slice";
import logoutReducer from "../auth/logout/logout_slice";               // single-device logout
import logoutAllReducer from "../auth/logout_all/logout_all_slice";    // logout from all devices
import oauth2Reducer from "../auth/oauth2/oauth2_slice";
import verifyAccountReducer from "../auth/verify_account/verify_account_slice";

// Import reducers for password reset slices
import passwordResetRequestReducer from "../auth/password_reset_request/password_reset_request_slice";
import passwordResetConfirmReducer from "../auth/password_reset_confirm/password_reset_confirm_slice";

// ---------------------------- Store Setup ----------------------------
// Create the Redux store with all reducers mapped to slice names
export const store = configureStore({
    reducer: {
        // 'login' slice manages authentication state (tokens, loading, error)
        login: loginReducer,
        // 'signup' slice manages signup state (loading, error, success)
        signup: signupReducer,
        // 'logout' slice manages single-device logout state
        logout: logoutReducer,
        // 'logoutAll' slice manages logout from all devices state
        logoutAll: logoutAllReducer,
        // 'oauth2' slice manages OAuth2 login state (tokens, loading, error)
        oauth2: oauth2Reducer,
        // 'verifyAccount' slice manages account verification state
        verifyAccount: verifyAccountReducer,
        // 'passwordResetRequest' slice manages sending password reset emails
        passwordResetRequest: passwordResetRequestReducer,
        // 'passwordResetConfirm' slice manages confirming new passwords
        passwordResetConfirm: passwordResetConfirmReducer,
    },
});

// ---------------------------- Types ----------------------------
// RootState represents the entire Redux state tree
// Helps TypeScript understand the shape of the state when using useSelector
export type RootState = ReturnType<typeof store.getState>;

// AppDispatch represents the Redux dispatch function with all slice actions/thunks
// Ensures correct typing when dispatching actions
export type AppDispatch = typeof store.dispatch;
