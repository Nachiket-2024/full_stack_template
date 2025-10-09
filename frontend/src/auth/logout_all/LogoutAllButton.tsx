// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX syntax and side effects
import React, { useEffect } from "react";

// Import Redux hooks for dispatching actions and accessing state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for strongly-typed useSelector
import type { TypedUseSelectorHook } from "react-redux";

// Import React Router hook for navigation
import { useNavigate } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------
// Type-only imports for store typing
import type { RootState, AppDispatch } from "../../store/store";

// Import async thunk and action to clear logout-all state
import { logoutAllDevices, clearLogoutAllState } from "./logout_all_slice";

// Import presentational button component
import LogoutAllButtonComponent from "./LogoutAllButtonComponent";

// ---------------------------- Typed Selector Hook ----------------------------
// Create typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- LogoutAllButton Container ----------------------------
// Container component connecting Redux state and handlers to UI
const LogoutAllButton: React.FC = () => {
    // ---------------------------- Redux ----------------------------
    // Typed dispatch function
    const dispatch = useDispatch<AppDispatch>();

    // Extract loading, error, successMessage from logoutAll slice
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.logoutAll
    );

    // ---------------------------- Router ----------------------------
    // Hook to navigate programmatically
    const navigate = useNavigate();

    // ---------------------------- Event Handlers ----------------------------
    // Handle logout-all button click
    const handleLogoutAll = () => {
        dispatch(logoutAllDevices()); // Dispatch logout-all thunk
    };

    // ---------------------------- Side Effect ----------------------------
    // Redirect user to login page when logout-all succeeds
    useEffect(() => {
        if (successMessage) {
            navigate("/login");                  // Navigate to login page
            dispatch(clearLogoutAllState());     // Reset state after redirect
        }
    }, [successMessage, navigate, dispatch]);

    // ---------------------------- Render ----------------------------
    // Render styled LogoutAllButtonComponent with props
    return (
        <LogoutAllButtonComponent
            loading={loading}               // Pass loading state
            error={error}                   // Pass error message
            successMessage={successMessage} // Pass success message
            onLogoutAll={handleLogoutAll}   // Pass logout-all handler
        />
    );
};

// ---------------------------- Export ----------------------------
// Export LogoutAllButton container component
export default LogoutAllButton;
