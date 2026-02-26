// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX syntax and functional components
import React from "react";

// Import Redux useSelector hook to access state
import { useSelector } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Import TypedUseSelectorHook for TypeScript typing
import type { TypedUseSelectorHook } from "react-redux";

// Import RootState type for strongly-typed Redux state
import type { RootState } from "../../store/store";

// Import application settings, including API base URL
import settings from "../../core/settings";

// Import presentational component that renders the button and UI
import OAuth2LoginButtonComponent from "./OAuth2LoginButtonComponent";

// ---------------------------- Props Interface ----------------------------
/**
 * OAuth2ButtonProps
 * Props for the container component:
 * 1. onSuccess: optional callback after successful login
 * 2. onAttempt: optional callback triggered when a login attempt occurs
 */
interface OAuth2ButtonProps {
    onSuccess?: () => void;  // Step 1: callback after successful login
    onAttempt?: () => void;  // Step 2: callback on login attempt
}

// ---------------------------- Typed Selector Hook ----------------------------
// Create a typed selector for strong typing when accessing Redux state
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- OAuth2LoginButton Container ----------------------------
/**
 * OAuth2LoginButton
 * Container component handling OAuth2 login state:
 * 1. Reads authentication/error state from Redux
 * 2. Provides login handler to trigger OAuth2 redirect
 * 3. Passes state and handler down to presentational component
 */
const OAuth2LoginButton: React.FC<OAuth2ButtonProps> = ({ onAttempt }) => {
    // ---------------------------- State Selection ----------------------------
    // Step 1: Select OAuth2 slice state
    const { error, isAuthenticated, user } = useAppSelector(state => state.oauth2);

    // Step 2: Select global authentication state and coerce to boolean
    const globalAuthRaw = useAppSelector(state => state.currentUser.isAuthenticated);
    const globalAuth: boolean = !!globalAuthRaw; // Convert null/undefined to false

    // ---------------------------- Methods ----------------------------
    /**
     * handleLogin
     * Input: none
     * Process:
     *   1. Call optional onAttempt callback
     *   2. Redirect browser to Google OAuth2 login endpoint
     * Output: void
     */
    const handleLogin = () => {
        onAttempt?.(); // Step 1: notify parent of login attempt
        window.location.href = `${settings.apiBaseUrl}/auth/oauth2/login/google`; // Step 2: perform OAuth2 redirect
    };

    // ---------------------------- Render ----------------------------
    /**
     * Render presentational component with state and callbacks
     */
    return (
        <OAuth2LoginButtonComponent
            error={error}                      // Pass error message
            isAuthenticated={isAuthenticated}  // Pass OAuth2 auth state
            user={user}                         // Pass OAuth2 user info
            globalAuth={globalAuth}             // Pass global auth state (boolean)
            onLogin={handleLogin}               // Pass login handler
        />
    );
};

// ---------------------------- Export ----------------------------
// Export container component for use in login pages
export default OAuth2LoginButton;