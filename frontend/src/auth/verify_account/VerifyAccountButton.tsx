// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX syntax
import React, { useEffect } from "react";

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
    token: string;          // Token for account verification
    email: string;          // Email associated with account
    onSuccess?: () => void; // Optional callback after successful verification
}

// Functional component to handle account verification
// Methods:
// 1. handleVerify - Dispatches verifyAccount thunk
// 2. handleClear - Resets verification state
// 3. useEffect - Triggers onSuccess callback after successful verification
const VerifyAccountButton: React.FC<VerifyAccountButtonProps> = ({ token, email, onSuccess }) => {

    // ---------------------------- Redux ----------------------------
    // Get typed dispatch function
    const dispatch = useDispatch<AppDispatch>();

    // Get verify account state from Redux store
    const { loading, error, successMessage } = useAppSelector((state) => state.verifyAccount);

    // ---------------------------- Effects ----------------------------
    /**
     * Input:
     *   1. successMessage from Redux state
     *   2. onSuccess callback function (optional)
     * Process:
     *   1. Watch for changes in successMessage
     *   2. If successMessage exists and onSuccess provided, call onSuccess
     * Output:
     *   1. Trigger onSuccess callback after successful verification
     */
    useEffect(() => {
        // Step 1: Check for success message and optional callback
        if (successMessage && onSuccess) {
            onSuccess(); // Step 1a: Trigger success callback
        }
    }, [successMessage, onSuccess]);

    // ---------------------------- Event Handlers ----------------------------
    /**
     * handleVerify - Dispatch thunk to verify account
     * Input: token and email from props
     * Process:
     *   1. Dispatch verifyAccount thunk with payload
     * Output: Redux state updates (loading, successMessage, error)
     */
    const handleVerify = () => {
        dispatch(verifyAccount({ token, email })); // Step 1
    };

    /**
     * handleClear - Reset verification messages and state
     * Input: None
     * Process:
     *   1. Dispatch clearVerifyAccountState action
     * Output: Redux state reset (loading=false, error=null, successMessage=null)
     */
    const handleClear = () => {
        dispatch(clearVerifyAccountState()); // Step 1
    };

    // ---------------------------- Render ----------------------------
    /**
     * Input: Redux state (loading, error, successMessage)
     * Process:
     *   1. Render "Verify Account" button with loading state
     *   2. Display error message if present
     *   3. Display success message if present
     *   4. Render "Clear" button to reset state
     * Output: JSX for account verification UI
     */
    return (
        <div>
            {/* Step 1: Verify account button */}
            <button onClick={handleVerify} disabled={loading}>
                {loading ? "Verifying..." : "Verify Account"}
            </button>

            {/* Step 2: Display error message if verification failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Step 3: Display success message if verification succeeded */}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            {/* Step 4: Button to clear state/messages */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export VerifyAccountButton component as default
export default VerifyAccountButton;
