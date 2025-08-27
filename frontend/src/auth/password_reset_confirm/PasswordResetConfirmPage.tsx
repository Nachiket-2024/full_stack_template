// ---------------------------- External Imports ----------------------------
import React from "react";

// ---------------------------- Internal Imports ----------------------------
// Import the Redux-connected password reset form
import PasswordResetConfirmForm from "./PasswordResetConfirmForm";

// ---------------------------- Component Definition ----------------------------
const PasswordResetConfirmPage: React.FC = () => {
    // ---------------------------- JSX Return ----------------------------
    return (
        // Wrapper div for consistent page styling
        <div className="auth-page-container">
            {/* Page heading */}
            <h1>Reset Password</h1>

            {/* Render the password reset confirmation form */}
            <PasswordResetConfirmForm />
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default PasswordResetConfirmPage;
