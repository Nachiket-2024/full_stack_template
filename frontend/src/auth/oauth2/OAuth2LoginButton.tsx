// ---------------------------- External Imports ----------------------------
// Import React and useEffect hook
import React, { useEffect } from "react";

// Import Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for typed useSelector hook
import type { TypedUseSelectorHook } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Type-only imports for store types
import type { RootState, AppDispatch } from "../../store/store";

// Import slice action to clear OAuth2 state
import { clearOAuth2State } from "./oauth2_slice";

// Import app settings (API base URL)
import settings from "../../core/settings";

// ---------------------------- Props Interface ----------------------------
// Props for OAuth2LoginButton component
interface OAuth2ButtonProps {
    onSuccess?: () => void; // Callback after successful login
}

// ---------------------------- Typed Selector Hook ----------------------------
// Create typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- OAuth2LoginButton Component ----------------------------
// Component to handle OAuth2 login (Google)
const OAuth2LoginButton: React.FC<OAuth2ButtonProps> = ({ onSuccess }) => {
    // ---------------------------- Redux ----------------------------
    // Get typed dispatch function
    const dispatch = useDispatch<AppDispatch>();
    // Get OAuth2 login state from Redux store
    const { loading, error, accessToken } = useAppSelector((state) => state.oauth2);

    // ---------------------------- Effect: redirect on success ----------------------------
    // Call onSuccess callback when login succeeds
    useEffect(() => {
        if (accessToken && onSuccess) {
            onSuccess();
        }
    }, [accessToken, onSuccess]);

    // ---------------------------- Event Handlers ----------------------------
    // Redirect to OAuth2 login endpoint
    const handleLogin = () => {
        window.location.href = `${settings.apiBaseUrl}/auth/oauth2/login/google`;
    };

    // Clear OAuth2 state in Redux store
    const handleClear = () => {
        dispatch(clearOAuth2State());
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
            {accessToken && <p style={{ color: "green" }}>Login successful!</p>}

            {/* Button to clear OAuth2 state */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export OAuth2LoginButton component as default
export default OAuth2LoginButton;
