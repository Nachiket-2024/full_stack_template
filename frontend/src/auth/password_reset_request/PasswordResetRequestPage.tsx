// ---------------------------- External Imports ----------------------------
// React core for component creation
import React from "react";

// ---------------------------- Internal Imports ----------------------------
// Import the Redux-connected form component for requesting a password reset
import PasswordResetRequestForm from "./PasswordResetRequestForm";

// ---------------------------- PasswordResetRequestPage Component ----------------------------
// Page component that wraps and displays the password reset request form
const PasswordResetRequestPage: React.FC = () => {
    // ---------------------------- Render ----------------------------
    return (
        // Step 1: Wrapper container for consistent page styling
        <div className="auth-page-container">
            {/* Step 2: Page heading */}
            <h1>Password Reset Request</h1>

            {/* Step 3: Render the password reset request form component */}
            <PasswordResetRequestForm />
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export PasswordResetRequestPage component for use in routing
export default PasswordResetRequestPage;
