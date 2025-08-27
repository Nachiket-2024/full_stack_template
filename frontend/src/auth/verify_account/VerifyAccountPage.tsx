// ---------------------------- External Imports ----------------------------
import React from "react";
import { useSearchParams } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------
import VerifyAccountButton from "./VerifyAccountButton";

// ---------------------------- Component Definition ----------------------------
const VerifyAccountPage: React.FC = () => {
    // Get query parameters from the URL
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token") || ""; // fallback to empty string
    const email = searchParams.get("email") || "";

    // ---------------------------- JSX Return ----------------------------
    return (
        <div className="auth-page-container">
            <h1>Verify Account</h1>

            {/* Render the button and pass required props */}
            <VerifyAccountButton token={token} email={email} />
        </div>
    );
};

export default VerifyAccountPage;
