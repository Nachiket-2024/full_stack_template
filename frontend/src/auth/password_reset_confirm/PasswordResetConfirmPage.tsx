// ---------------------------- External Imports ----------------------------
// Import React library for JSX/TSX syntax
import React from "react";

// ---------------------------- Internal Imports ----------------------------
// Import the Redux-connected password reset confirmation form component
import PasswordResetConfirmForm from "./PasswordResetConfirmForm";

// ---------------------------- Component Definition ----------------------------
// Page component for password reset confirmation
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
// Export PasswordResetConfirmPage as default
export default PasswordResetConfirmPage;
