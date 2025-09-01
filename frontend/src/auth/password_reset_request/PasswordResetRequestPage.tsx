// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX syntax
import React from "react";

// ---------------------------- Internal Imports ----------------------------
// Import the form component that handles sending the reset email
import PasswordResetRequestForm from "./PasswordResetRequestForm";

// ---------------------------- Component Definition ----------------------------
// Page component for requesting a password reset
const PasswordResetRequestPage: React.FC = () => {
    // ---------------------------- JSX Return ----------------------------
    return (
        // Wrapper div for consistent page styling
        <div className="auth-page-container">
            {/* Page heading */}
            <h1>Password Reset Request</h1>

            {/* Render the password reset request form */}
            <PasswordResetRequestForm />
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export PasswordResetRequestPage as default
export default PasswordResetRequestPage;
