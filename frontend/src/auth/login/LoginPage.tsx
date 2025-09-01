// ---------------------------- External Imports ----------------------------
// Import React library for JSX/TSX syntax
import React from "react";
import { useNavigate } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------
// Import normal login form component
import LoginForm from "./LoginForm";

// Import OAuth2 login button component
import OAuth2Button from "../oauth2/OAuth2LoginButton";

// ---------------------------- Component Definition ----------------------------
// LoginPage component renders login options for users
const LoginPage: React.FC = () => {
    // Hook to programmatically navigate after login
    const navigate = useNavigate();

    // Callback function to redirect to dashboard after successful login
    const handleLoginSuccess = () => {
        navigate("/dashboard", { replace: true });
    };

    return (
        // Container for the authentication page
        <div className="auth-page-container">
            {/* Page title */}
            <h1>Login</h1>

            {/* Render normal login form with onSuccess callback */}
            <LoginForm onSuccess={handleLoginSuccess} />

            {/* Separator between normal login and OAuth2 login */}
            <hr style={{ margin: "20px 0" }} />

            {/* Render OAuth2 login button with onSuccess callback */}
            <OAuth2Button onSuccess={handleLoginSuccess} />
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export LoginPage as default
export default LoginPage;
