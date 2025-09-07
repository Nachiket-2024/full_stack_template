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

// Import slice actions to manage OAuth2 state
import {
    clearUserSession,
    setUserSession,
    setOAuth2Error,
    setOAuth2Loading,
} from "./oauth2_slice";

// Import app settings (API base URL)
import settings from "../../core/settings";

// Import API function to fetch current user session
import { getCurrentUserApi } from "../../api/auth_api";

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
    const dispatch = useDispatch<AppDispatch>();
    const { loading, error, isAuthenticated, user } = useAppSelector(
        (state) => state.oauth2
    );

    // ---------------------------- Effect: verify session after redirect ----------------------------
    useEffect(() => {
        const verifySession = async () => {
            try {
                dispatch(setOAuth2Loading());
                const response = await getCurrentUserApi(); // cookie sent automatically
                if (response.data) {
                    dispatch(setUserSession(response.data));
                    if (onSuccess) onSuccess();
                }
            } catch (err: any) {
                dispatch(setOAuth2Error("Failed to verify session"));
            }
        };

        // Run only once on mount (handles post-OAuth2 redirect)
        verifySession();
    }, [dispatch, onSuccess]);

    // ---------------------------- Event Handlers ----------------------------
    const handleLogin = () => {
        // Redirect user to backend OAuth2 login URL
        window.location.href = `${settings.apiBaseUrl}/auth/oauth2/login/google`;
    };

    const handleClear = () => {
        // Clear user session in Redux store
        dispatch(clearUserSession());
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
            {isAuthenticated && user && (
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
export default OAuth2LoginButton;
