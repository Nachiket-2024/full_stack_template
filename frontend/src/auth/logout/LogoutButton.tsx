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
    const dispatch = useDispatch<AppDispatch>();
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.logout
    );

    // ---------------------------- Router ----------------------------
    const navigate = useNavigate();

    // ---------------------------- Event Handlers ----------------------------
    const handleLogout = () => {
        dispatch(logoutUser());
    };

    // ---------------------------- Side Effect ----------------------------
    // Redirect to login when logout succeeds
    useEffect(() => {
        if (successMessage) {
            navigate("/login");
        }
    }, [successMessage, navigate]);

    // ---------------------------- Render ----------------------------
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
export default LogoutButton;
