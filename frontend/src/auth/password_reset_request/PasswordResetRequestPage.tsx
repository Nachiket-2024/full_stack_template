// ---------------------------- External Imports ----------------------------
import React from "react";

// ---------------------------- Internal Imports ----------------------------
// Import the form component that handles sending the reset email
import PasswordResetRequestForm from "./PasswordResetRequestForm";

// ---------------------------- Component Definition ----------------------------
// Define the PasswordResetRequestPage functional component
const PasswordResetRequestPage: React.FC = () => {
    // ---------------------------- JSX Return ----------------------------
    return (
        // Wrapper div for consistent page styling
        <div className="auth-page-container">
            {/* Page heading */}
            <h1>Password Reset Request</h1>

            {/* Render the form component */}
            <PasswordResetRequestForm />
        </div>
    );
};

// Export the component as default to use in routing
export default PasswordResetRequestPage;
