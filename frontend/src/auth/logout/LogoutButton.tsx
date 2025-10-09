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

// Import async thunk to logout user
import { logoutUser } from "./logout_slice";

// Import styled button component to separate UI from logic
import LogoutButtonComponent from "./LogoutButtonComponent";

// ---------------------------- Typed Selector Hook ----------------------------
// Create typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- LogoutButton Container ----------------------------
// Container component connecting Redux state and handlers to UI
const LogoutButton: React.FC = () => {
    // ---------------------------- Redux ----------------------------
    // Typed dispatch function
    const dispatch = useDispatch<AppDispatch>();

    // Extract loading, error, successMessage from logout slice
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.logout
    );

    // ---------------------------- Router ----------------------------
    // Hook to navigate programmatically
    const navigate = useNavigate();

    // ---------------------------- Event Handlers ----------------------------
    // Handle logout button click
    const handleLogout = () => {
        dispatch(logoutUser()); // Dispatch logout thunk
    };

    // ---------------------------- Side Effect ----------------------------
    // Redirect user to login page when logout succeeds
    useEffect(() => {
        if (successMessage) {
            navigate("/login"); // Navigate to login page
        }
    }, [successMessage, navigate]);

    // ---------------------------- Render ----------------------------
    // Render styled LogoutButtonComponent with props
    return (
        <LogoutButtonComponent
            loading={loading}               // Pass loading state
            error={error}                   // Pass error message
            successMessage={successMessage} // Pass success message
            onLogout={handleLogout}         // Pass logout handler
        />
    );
};

// ---------------------------- Export ----------------------------
// Export LogoutButton container component
export default LogoutButton;
