// ---------------------------- External Imports ----------------------------
// Import React for component and hooks
import React from "react";

// Import hooks from React Router for URL params and navigation
import { useSearchParams, useNavigate } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------
// Import verification button component
import VerifyAccountButton from "./VerifyAccountButton";

// ---------------------------- VerifyAccountPage Component ----------------------------
// Functional component to display account verification UI
// Methods:
// 1. handleSuccessRedirect - Navigates to login page after successful verification
const VerifyAccountPage: React.FC = () => {

    // ---------------------------- Hooks ----------------------------
    /**
     * Input: None (URL search params are automatically available)
     * Process:
     *   1. Get query parameters from the URL
     *   2. Setup navigate function for programmatic routing
     *   3. Extract token and email parameters with fallback values
     * Output:
     *   1. token and email strings from URL
     *   2. navigate function for redirection
     */
    const [searchParams] = useSearchParams(); // Step 1: URL query parameters
    const navigate = useNavigate();           // Step 2: Navigation function
    const token = searchParams.get("token") || ""; // Step 3a: Extract token
    const email = searchParams.get("email") || ""; // Step 3b: Extract email

    // ---------------------------- Handlers ----------------------------
    /**
     * handleSuccessRedirect - Callback to redirect user after successful verification
     * Input: None
     * Process:
     *   1. Navigate to "/login" route
     *   2. Replace current history entry to prevent back navigation
     * Output: User redirected to login page
     */
    const handleSuccessRedirect = () => {
        navigate("/login", { replace: true }); // Step 1 & 2
    };

    // ---------------------------- JSX Return ----------------------------
    /**
     * Input: token, email, handleSuccessRedirect
     * Process:
     *   1. Render container div for page layout
     *   2. Display heading "Verify Account"
     *   3. Render VerifyAccountButton with token, email, and success callback
     * Output: JSX.Element for the verification page
     */
    return (
        <div className="auth-page-container">
            {/* Step 2: Page heading */}
            <h1>Verify Account</h1>

            {/* Step 3: Render verification button */}
            <VerifyAccountButton
                token={token}
                email={email}
                onSuccess={handleSuccessRedirect}
            />
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export VerifyAccountPage as default for routing
export default VerifyAccountPage;
