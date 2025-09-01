// ---------------------------- External Imports ----------------------------
// Import React and useState hook for component state
import React, { useState } from "react";

// Import Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for typed useSelector hook
import type { TypedUseSelectorHook } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Import type-only RootState and AppDispatch from Redux store
import type { RootState, AppDispatch } from "../../store/store";

// Import actions from password reset request slice
import { requestPasswordReset, clearPasswordResetRequestState } from "./password_reset_request_slice";

// ---------------------------- Typed Selector Hook ----------------------------
// Create typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- PasswordResetRequestForm Component ----------------------------
// Component to handle password reset request
const PasswordResetRequestForm: React.FC = () => {
    // ---------------------------- Local State ----------------------------
    // State for email input
    const [email, setEmail] = useState("");

    // ---------------------------- Redux ----------------------------
    // Get typed dispatch function
    const dispatch = useDispatch<AppDispatch>();
    // Get password reset request state from Redux store
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.passwordResetRequest
    );

    // ---------------------------- Event Handlers ----------------------------
    // Handle form submission to request password reset
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        dispatch(requestPasswordReset({ email }));
    };

    // Clear form state and messages
    const handleClear = () => {
        dispatch(clearPasswordResetRequestState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            {/* Form title */}
            <h2>Password Reset Request</h2>

            {/* Password reset request form */}
            <form onSubmit={handleSubmit}>
                {/* Email input */}
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    required
                />

                {/* Submit button */}
                <button type="submit" disabled={loading}>
                    {loading ? "Requesting..." : "Request Password Reset"}
                </button>
            </form>

            {/* Display error message if request failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if request succeeded */}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            {/* Clear button to reset form and messages */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export PasswordResetRequestForm as default
export default PasswordResetRequestForm;
