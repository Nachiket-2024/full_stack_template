// ---------------------------- External Imports ----------------------------
import React from "react";

// ---------------------------- Internal Imports ----------------------------
import LoginForm from "./LoginForm";
import OAuth2Button from "../oauth2/OAuth2LoginButton";

// ---------------------------- Component Definition ----------------------------
const LoginPage: React.FC = () => {
    return (
        <div className="auth-page-container">
            <h1>Login</h1>

            {/* Normal login form */}
            <LoginForm />

            <hr style={{ margin: "20px 0" }} />

            {/* OAuth2 login button with required 'provider' prop */}
            <OAuth2Button />
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default LoginPage;
