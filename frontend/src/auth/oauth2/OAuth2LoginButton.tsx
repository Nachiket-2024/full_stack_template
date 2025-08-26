// ---------------------------- External Imports ----------------------------
import React from "react";
import { useDispatch, useSelector } from "react-redux";

// Type-only imports for Redux
import type { TypedUseSelectorHook } from "react-redux";
import type { RootState, AppDispatch } from "@/store/store";

// ---------------------------- Internal Imports ----------------------------
import { oauth2Login, clearOAuth2State } from "./oauth2_slice";

// ---------------------------- Typed Selector Hook ----------------------------
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- OAuth2LoginButton Component ----------------------------
interface OAuth2LoginButtonProps {
    provider: "google" | "facebook"; // Extendable to other providers
    buttonText?: string;
}

const OAuth2LoginButton: React.FC<OAuth2LoginButtonProps> = ({
    provider,
    buttonText,
}) => {
    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();
    const { loading, error, accessToken } = useAppSelector(
        (state) => state.oauth2
    );

    // ---------------------------- Event Handlers ----------------------------
    const handleLogin = () => {
        // Dispatch OAuth2 login thunk
        dispatch(oauth2Login({ provider }));
    };

    const handleClear = () => {
        dispatch(clearOAuth2State());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            <button onClick={handleLogin} disabled={loading}>
                {loading ? "Logging in..." : buttonText || `Login with ${provider}`}
            </button>

            {/* Display error if OAuth2 login fails */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display token info if login succeeded */}
            {accessToken && <p style={{ color: "green" }}>Login successful!</p>}

            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default OAuth2LoginButton;
