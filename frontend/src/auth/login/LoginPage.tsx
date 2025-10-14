// ---------------------------- External Imports ----------------------------
// Import React library for JSX/TSX syntax
import React from "react";

// Import React Router hooks and components for navigation
import { useNavigate, Link, Navigate } from "react-router-dom";

// Import Redux hooks for state access and dispatch
import { useSelector, useDispatch } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Import standard login form component
import LoginForm from "./LoginForm";

// Import OAuth2 login button component
import OAuth2Button from "../oauth2/OAuth2LoginButton";

// Import RootState type from your Redux store
import type { RootState, AppDispatch } from "../../store/store";

// Import action to clear OAuth2 user session (resets error, user, loading)
import { clearUserSession } from "../oauth2/oauth2_slice";

// ---------------------------- Component Definition ----------------------------
// LoginPage component renders login options for users
const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch<AppDispatch>();

    // ---------------------------- Redux State ----------------------------
    const { isAuthenticated, loading, error } = useSelector(
        (state: RootState) => state.oauth2
    );

    // ---------------------------- Local State ----------------------------
    // Track whether user actually attempted to login
    const [loginAttempted, setLoginAttempted] = React.useState(false);

    // ---------------------------- Clear stale errors on mount ----------------------------
    React.useEffect(() => {
        dispatch(clearUserSession()); // reset error, user, and loading on page load
        setLoginAttempted(false);     // ensure attempt flag is reset
    }, [dispatch]);

    // ---------------------------- Redirect Logic ----------------------------
    if (loading) {
        return <div>Loading...</div>;
    }

    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace />;
    }

    // ---------------------------- Callbacks ----------------------------
    // Callback function to redirect user to dashboard after successful login
    const handleLoginSuccess = () => {
        setLoginAttempted(false); // reset after success
        navigate("/dashboard", { replace: true });
    };

    // Callback function to mark that a login attempt was made
    const handleLoginAttempt = () => {
        setLoginAttempted(true);
    };

    // ---------------------------- Render ----------------------------
    return (
        <div className="auth-page-container">
            <h1>Login</h1>

            {/* Optional error display */}
            {error && loginAttempted && (
                <div className="auth-error" style={{ color: "red", marginBottom: "10px" }}>
                    {error}
                </div>
            )}

            {/* Standard login form */}
            <LoginForm
                onSuccess={handleLoginSuccess}
                onAttempt={handleLoginAttempt} // track login attempts
            />

            <hr style={{ margin: "20px 0" }} />

            {/* OAuth2 login button */}
            <OAuth2Button
                onSuccess={handleLoginSuccess}
                onAttempt={handleLoginAttempt} // track OAuth2 attempts
            />

            {/* Signup link */}
            <p style={{ marginTop: "20px" }}>
                Don’t have an account?{" "}
                <Link to="/signup" style={{ color: "blue", textDecoration: "underline" }}>
                    Sign Up
                </Link>
            </p>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export LoginPage component for use in routing
export default LoginPage;
