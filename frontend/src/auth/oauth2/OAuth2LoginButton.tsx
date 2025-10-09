// ---------------------------- External Imports ----------------------------
// Import React for creating functional components
import React from "react";

// Import Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for strongly-typed selector
import type { TypedUseSelectorHook } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Type-only imports for Redux store types
import type { RootState, AppDispatch } from "../../store/store";

// Import action to clear OAuth2 user session
import { clearUserSession } from "./oauth2_slice";

// Import app settings for API base URL
import settings from "../../core/settings";

// ---------------------------- Props Interface ----------------------------
// Props for OAuth2LoginButton component
interface OAuth2ButtonProps {
    // Optional callback after successful login
    onSuccess?: () => void;
}

// ---------------------------- Typed Selector Hook ----------------------------
// Create typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- OAuth2LoginButton Component ----------------------------
// Component: Handles OAuth2 login (Google)
// ---------------------------------------------------------------------------
// Methods:
//   1. handleLogin()  → Redirect user to OAuth2 login endpoint
//   2. handleClear()  → Clear current OAuth2 session from Redux
// ---------------------------------------------------------------------------
const OAuth2LoginButton: React.FC<OAuth2ButtonProps> = ({ onSuccess }) => {
    // ---------------------------- Redux ----------------------------
    // Typed dispatch function
    const dispatch = useDispatch<AppDispatch>();

    // Access OAuth2 slice for UI feedback
    const { loading, error, isAuthenticated, user } = useAppSelector(
        (state) => state.oauth2
    );

    // Access global currentUser slice (for cross-check)
    const { isAuthenticated: globalAuth } = useAppSelector(
        (state) => state.currentUser
    );

    // ---------------------------- Methods ----------------------------
    /**
     * handleLogin
     * ----------------------------
     * Input: None
     * Process:
     *   1. Redirect user to backend OAuth2 login URL.
     * Output: Redirects browser, does not return.
     */
    const handleLogin = () => {
        // Step 1: Redirect to backend for Google OAuth2 login
        window.location.href = `${settings.apiBaseUrl}/auth/oauth2/login/google`;
    };

    /**
     * handleClear
     * ----------------------------
     * Input: None
     * Process:
     *   1. Clear user session state from Redux.
     *   2. Optionally trigger onSuccess callback.
     * Output: Redux state reset, callback executed if provided.
     */
    const handleClear = () => {
        // Step 1: Dispatch Redux action to clear local session
        dispatch(clearUserSession());

        // Step 2: Call callback if provided
        if (onSuccess) onSuccess();
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            {/* Button to start OAuth2 login */}
            <button onClick={handleLogin} disabled={loading}>
                {loading ? "Logging in..." : "Login with Google"}
            </button>

            {/* Display error message if login failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if login succeeded */}
            {(isAuthenticated || globalAuth) && user && (
                <p style={{ color: "green" }}>
                    Welcome, {user.email}! (role: {user.role})
                </p>
            )}

            {/* Button to clear user session */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export OAuth2LoginButton component as default
export default OAuth2LoginButton;
