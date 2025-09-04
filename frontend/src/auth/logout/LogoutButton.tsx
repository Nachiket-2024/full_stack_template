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

// Import async thunk and action to clear logout state from logout slice
import { logoutUser } from "./logout_slice";

// Import styled LogoutButtonComponent to separate UI from container logic
import LogoutButtonComponent from "./LogoutButtonComponent";

// ---------------------------- Typed Selector Hook ----------------------------
// Create a typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- LogoutButton Container ----------------------------
// Container component to connect Redux state and handlers to styled button
const LogoutButton: React.FC = () => {
    // ---------------------------- Redux ----------------------------
    // Initialize dispatch function typed with AppDispatch
    const dispatch = useDispatch<AppDispatch>();
    // Select logout state from Redux store
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.logout
    );

    // ---------------------------- Event Handlers ----------------------------
    // Handle logout by dispatching the logout async thunk
    const handleLogout = () => {
        dispatch(logoutUser());
    };

    // ---------------------------- Render ----------------------------
    // Pass Redux state and event handlers as props to styled component
    return (
        <LogoutButtonComponent
            loading={loading}
            error={error}
            successMessage={successMessage}
            onLogout={handleLogout}
        />
    );
};

// ---------------------------- Export ----------------------------
// Export LogoutButton container as default
export default LogoutButton;
