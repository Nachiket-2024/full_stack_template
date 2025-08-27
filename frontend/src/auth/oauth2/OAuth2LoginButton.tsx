// ---------------------------- External Imports ----------------------------
import React from "react";
import { useDispatch, useSelector } from "react-redux";

// Type-only imports for Redux
import type { TypedUseSelectorHook } from "react-redux";
import type { RootState, AppDispatch } from "@/store/store";

// ---------------------------- Internal Imports ----------------------------
import { clearOAuth2State } from "./oauth2_slice";

// ---------------------------- Typed Selector Hook ----------------------------
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- OAuth2LoginButton Component ----------------------------
const OAuth2LoginButton: React.FC = () => {
    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();
    const { loading, error, accessToken } = useAppSelector(
        (state) => state.oauth2
    );

    // ---------------------------- Event Handlers ----------------------------
    const handleLogin = () => {
        // Directly redirect to Google OAuth2 login endpoint
        window.location.href = "/auth/oauth2/login/google";
    };

    const handleClear = () => {
        // Clear Redux OAuth2 state
        dispatch(clearOAuth2State());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            <button onClick={handleLogin} disabled={loading}>
                {loading ? "Logging in..." : "Login with Google"}
            </button>

            {/* Display error if OAuth2 login fails */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display token info if login succeeded */}
            {accessToken && <p style={{ color: "green" }}>Login successful!</p>}

            {/* Clear state button */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default OAuth2LoginButton;
