// ---------------------------- External Imports ----------------------------
// Import React to create the functional component
import React from "react";

// ---------------------------- Internal Imports ----------------------------
// Import the SignupForm component from the same folder
import SignupForm from "./SignupForm";

// ---------------------------- Signup Page Component ----------------------------
// Functional component to render the signup page
// Methods:
// 1. render - Returns the JSX for the signup page including heading and form
const SignupPage: React.FC = () => {

    // ---------------------------- Render Method ----------------------------
    // Returns the JSX structure for the signup page
    // Input: None (props could be added if needed in future)
    // Process:
    //     1. Wrap the page content in a container div for styling/layout.
    //     2. Add a heading element for the page title.
    //     3. Render the SignupForm component inside the page.
    // Output: JSX.Element representing the signup page
    return (
        // Step 1: Wrapper div for the page; can use CSS class for styling/layout
        <div className="auth-page-container">

            {/* Step 2: Page heading */}
            <h1>Sign Up</h1>

            {/* Step 3: Render the SignupForm component */}
            <SignupForm />
        </div>
    );
};

// ---------------------------- Component Export ----------------------------
// Export the component as default to use in routing or higher-level layout
export default SignupPage;
