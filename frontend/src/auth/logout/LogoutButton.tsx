// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX syntax
import React from "react";

// Import hooks for Redux state and dispatch
import { useDispatch, useSelector } from "react-redux";

// Type-only imports for typing Redux hooks
import type { TypedUseSelectorHook } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Import type-only RootState and AppDispatch from Redux store
import type { RootState, AppDispatch } from "../../store/store";

// Import logout actions from logout slice
import { logoutUser, logoutAllDevices, clearLogoutState } from "./logout_slice";

// ---------------------------- Typed Selector Hook ----------------------------
// Create typed useSelector hook for better TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- LogoutButton Component ----------------------------
// Component to render logout buttons and handle logout actions
const LogoutButton: React.FC = () => {
    // ---------------------------- Redux ----------------------------
    // Get Redux dispatch function typed with AppDispatch
    const dispatch = useDispatch<AppDispatch>();
    // Get logout state from Redux store
    const { loading, error, successMessage } = useAppSelector((state) => state.logout);

    // ---------------------------- Event Handlers ----------------------------
    // Logout from current device
    const handleLogout = () => {
        dispatch(logoutUser()); // no payload anymore
    };

    // Logout from all devices
    const handleLogoutAll = () => {
        dispatch(logoutAllDevices()); // no payload anymore
    };

    // Clear logout messages and state
    const handleClear = () => {
        dispatch(clearLogoutState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            {/* Logout current device button */}
            <button onClick={handleLogout} disabled={loading}>
                {loading ? "Logging out..." : "Logout"}
            </button>

            {/* Logout all devices button */}
            <button onClick={handleLogoutAll} disabled={loading}>
                {loading ? "Logging out all..." : "Logout All Devices"}
            </button>

            {/* Display error message if any */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if any */}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            {/* Button to clear messages */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export LogoutButton component as default
export default LogoutButton;
