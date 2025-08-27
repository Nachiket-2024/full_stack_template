// ---------------------------- External Imports ----------------------------
// Import React to create the functional component
import React from "react";

// ---------------------------- Internal Imports ----------------------------
// Import the SignupForm component from the same folder
import SignupForm from "./SignupForm";

// ---------------------------- Component Definition ----------------------------
// Define the SignupPage functional component
const SignupPage: React.FC = () => {
    // ---------------------------- JSX Return ----------------------------
    return (
        // Wrapper div for the page; can use CSS class for styling/layout
        <div className="auth-page-container">
            {/* Page heading */}
            <h1>Sign Up</h1>

            {/* Render the SignupForm component */}
            <SignupForm />
        </div>
    );
};

// Export the component as default to use in routing
export default SignupPage;
