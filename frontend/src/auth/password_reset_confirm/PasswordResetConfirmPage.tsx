// ---------------------------- External Imports ----------------------------
// React core for component creation
import React from "react";

// ---------------------------- Internal Imports ----------------------------
// Import the Redux-connected form component for confirming password reset
import PasswordResetConfirmForm from "./PasswordResetConfirmForm";

// ---------------------------- PasswordResetConfirmPage Component ----------------------------
// Page component that wraps and displays the password reset confirmation form
const PasswordResetConfirmPage: React.FC = () => {
    // ---------------------------- Render ----------------------------
    return (
        // Step 1: Wrapper container for consistent page styling
        <div className="auth-page-container">
            {/* Step 2: Page heading */}
            <h1>Reset Password</h1>

            {/* Step 3: Render the password reset confirmation form component */}
            <PasswordResetConfirmForm />
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export PasswordResetConfirmPage component for use in routing
export default PasswordResetConfirmPage;
