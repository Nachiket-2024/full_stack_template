// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX syntax
import React from "react";

// Import Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for typed useSelector hook
import type { TypedUseSelectorHook } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Type-only imports for store types
import type { RootState, AppDispatch } from "../../store/store";

// Import verify account thunk and slice actions
import { verifyAccount, clearVerifyAccountState } from "./verify_account_slice";

// ---------------------------- Typed Selector Hook ----------------------------
// Create typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- VerifyAccountButton Component ----------------------------
// Props for VerifyAccountButton component
interface VerifyAccountButtonProps {
    token: string; // Token for account verification
    email: string; // Email associated with account
}

// Component to handle account verification
const VerifyAccountButton: React.FC<VerifyAccountButtonProps> = ({ token, email }) => {
    // ---------------------------- Redux ----------------------------
    // Get typed dispatch function
    const dispatch = useDispatch<AppDispatch>();
    // Get verify account state from Redux store
    const { loading, error, successMessage } = useAppSelector((state) => state.verifyAccount);

    // ---------------------------- Event Handlers ----------------------------
    // Handle account verification
    const handleVerify = () => {
        dispatch(verifyAccount({ token, email }));
    };

    // Clear verification messages and state
    const handleClear = () => {
        dispatch(clearVerifyAccountState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            {/* Verify account button */}
            <button onClick={handleVerify} disabled={loading}>
                {loading ? "Verifying..." : "Verify Account"}
            </button>

            {/* Display error message if verification failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if verification succeeded */}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            {/* Button to clear state/messages */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export VerifyAccountButton component as default
export default VerifyAccountButton;
