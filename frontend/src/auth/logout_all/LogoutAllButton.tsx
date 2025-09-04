// ---------------------------- External Imports ----------------------------
// Import React to use JSX/TSX syntax in component
import React, { useEffect } from "react";

// Import hooks from react-redux for accessing and dispatching Redux state
import { useDispatch, useSelector } from "react-redux";

// Import type-only TypedUseSelectorHook for strongly-typed selector
import type { TypedUseSelectorHook } from "react-redux";

// Import React Router navigate hook for redirect
import { useNavigate } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------
// Import type-only RootState and AppDispatch from Redux store for typing hooks
import type { RootState, AppDispatch } from "../../store/store";

// Import async thunk and action to clear logout-all state from logout-all slice
import { logoutAllDevices, clearLogoutAllState } from "./logout_all_slice";

// Import presentational component to separate UI from container logic
import LogoutAllButtonComponent from "./LogoutAllButtonComponent";

// ---------------------------- Typed Selector Hook ----------------------------
// Create a typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- LogoutAllButton Container ----------------------------
// Container component to connect Redux state and handlers to styled button
const LogoutAllButton: React.FC = () => {
    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.logoutAll
    );

    // ---------------------------- Router ----------------------------
    const navigate = useNavigate();

    // ---------------------------- Event Handlers ----------------------------
    const handleLogoutAll = () => {
        dispatch(logoutAllDevices());
    };

    // ---------------------------- Side Effect ----------------------------
    // Redirect to login when logout-all succeeds
    useEffect(() => {
        if (successMessage) {
            navigate("/login");
            dispatch(clearLogoutAllState()); // Reset state after redirect
        }
    }, [successMessage, navigate, dispatch]);

    // ---------------------------- Render ----------------------------
    return (
        <LogoutAllButtonComponent
            loading={loading}
            error={error}
            successMessage={successMessage}
            onLogoutAll={handleLogoutAll}
        />
    );
};

// ---------------------------- Export ----------------------------
// Export LogoutAllButton container as default
export default LogoutAllButton;
