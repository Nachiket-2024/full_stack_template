// ---------------------------- External Imports ----------------------------
// Import React to use JSX/TSX syntax in component
import React from "react";

// Import hooks from react-redux for accessing and dispatching Redux state
import { useDispatch, useSelector } from "react-redux";

// Import type-only TypedUseSelectorHook for strongly-typed selector
import type { TypedUseSelectorHook } from "react-redux";

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
    // Initialize dispatch function typed with AppDispatch
    const dispatch = useDispatch<AppDispatch>();
    // Select logout-all state from Redux store
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.logoutAll
    );

    // ---------------------------- Event Handlers ----------------------------
    // Handle logout-all button click by dispatching logoutAllDevices async thunk
    const handleLogoutAll = () => {
        dispatch(logoutAllDevices());
    };

    // Handle clear button click by dispatching action to reset logout-all state
    const handleClear = () => {
        dispatch(clearLogoutAllState());
    };

    // ---------------------------- Render ----------------------------
    // Pass Redux state and event handlers as props to presentational component
    return (
        <LogoutAllButtonComponent
            loading={loading}
            error={error}
            successMessage={successMessage}
            onLogoutAll={handleLogoutAll}
            onClear={handleClear}
        />
    );
};

// ---------------------------- Export ----------------------------
// Export LogoutAllButton container as default
export default LogoutAllButton;
