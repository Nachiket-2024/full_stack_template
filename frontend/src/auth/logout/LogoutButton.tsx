// ---------------------------- External Imports ----------------------------
import React from "react";
import { useDispatch, useSelector } from "react-redux";

// Type-only imports for Redux
import type { TypedUseSelectorHook } from "react-redux";
import type { RootState, AppDispatch } from "../../store/store";

// ---------------------------- Internal Imports ----------------------------
import { logoutUser, logoutAllDevices, clearLogoutState } from "./logout_slice";

// ---------------------------- Typed Selector Hook ----------------------------
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- LogoutButton Component ----------------------------
interface LogoutButtonProps {
    refreshToken: string;
}

const LogoutButton: React.FC<LogoutButtonProps> = ({ refreshToken }) => {
    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();
    const { loading, error, successMessage } = useAppSelector((state) => state.logout);

    // ---------------------------- Event Handlers ----------------------------
    const handleLogout = () => {
        dispatch(logoutUser({ refresh_token: refreshToken }));
    };

    const handleLogoutAll = () => {
        dispatch(logoutAllDevices({ refresh_token: refreshToken }));
    };

    const handleClear = () => {
        dispatch(clearLogoutState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            <button onClick={handleLogout} disabled={loading}>
                {loading ? "Logging out..." : "Logout"}
            </button>
            <button onClick={handleLogoutAll} disabled={loading}>
                {loading ? "Logging out all..." : "Logout All Devices"}
            </button>

            {error && <p style={{ color: "red" }}>{error}</p>}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default LogoutButton;
