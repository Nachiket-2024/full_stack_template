// ---------------------------- External Imports ----------------------------
// Import core React library for building components
import React from "react";
// Import hooks from Redux for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only imports for Redux
// Typed hook for selecting state from the Redux store
import type { TypedUseSelectorHook } from "react-redux";
// Import RootState and AppDispatch types from the store
import type { RootState, AppDispatch } from "../../store/store";

// ---------------------------- Internal Imports ----------------------------
// Import action to clear OAuth2 state
import { clearOAuth2State } from "./oauth2_slice";
// Import global settings including API base URL
import settings from "../../core/settings";

// ---------------------------- Typed Selector Hook ----------------------------
// Create a typed selector hook for accessing the Redux store state
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- OAuth2LoginButton Component ----------------------------
// Define OAuth2LoginButton as a functional React component
const OAuth2LoginButton: React.FC = () => {
    // ---------------------------- Redux ----------------------------
    // Get the dispatch function with correct AppDispatch type
    const dispatch = useDispatch<AppDispatch>();
    // Extract loading, error, and accessToken from the oauth2 slice of state
    const { loading, error, accessToken } = useAppSelector(
        (state) => state.oauth2
    );

    // ---------------------------- Event Handlers ----------------------------
    // Handle login by redirecting to Google OAuth2 endpoint
    const handleLogin = () => {
        window.location.href = `${settings.apiBaseUrl}/auth/oauth2/login/google`;
    };

    // Handle clearing OAuth2 state by dispatching the clear action
    const handleClear = () => {
        dispatch(clearOAuth2State());
    };

    // ---------------------------- Render ----------------------------
    // Render UI elements for OAuth2 login
    return (
        <div>
            {/* Button for triggering Google login, disabled if loading */}
            <button onClick={handleLogin} disabled={loading}>
                {loading ? "Logging in..." : "Login with Google"}
            </button>

            {/* Display error message if login failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if access token exists */}
            {accessToken && <p style={{ color: "green" }}>Login successful!</p>}

            {/* Button for clearing OAuth2 state */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export OAuth2LoginButton component as default
export default OAuth2LoginButton;
