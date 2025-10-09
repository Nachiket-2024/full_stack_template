// ---------------------------- External Imports ----------------------------
// React core and useState hook for managing local component state
import React, { useState } from "react";

// Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for typed selector hook
import type { TypedUseSelectorHook } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Type-only RootState and AppDispatch for typed Redux hooks
import type { RootState, AppDispatch } from "../../store/store";

// Import async thunk and clear state action for password reset requests
import { requestPasswordReset, clearPasswordResetRequestState } from "./password_reset_request_slice";

// ---------------------------- Typed Selector Hook ----------------------------
// Create a strongly typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- PasswordResetRequestForm Component ----------------------------
// Handles the password reset request form for users
const PasswordResetRequestForm: React.FC = () => {
    // ---------------------------- Local State ----------------------------
    // Step 1: Store email input from the user
    const [email, setEmail] = useState("");

    // ---------------------------- Redux ----------------------------
    // Step 2: Get typed dispatch function
    const dispatch = useDispatch<AppDispatch>();
    // Step 3: Extract Redux state for password reset request
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.passwordResetRequest
    );

    // ---------------------------- Event Handlers ----------------------------
    /**
     * handleSubmit
     * ----------------------------
     * Input: Form submit event
     * Process:
     *   1. Prevent default form submission behavior.
     *   2. Dispatch async thunk to request password reset with the provided email.
     * Output: Redux state updated with loading/error/successMessage.
     */
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        dispatch(requestPasswordReset({ email }));
    };

    /**
     * handleClear
     * ----------------------------
     * Input: None
     * Process:
     *   1. Dispatch Redux action to reset password reset request state.
     * Output: Redux state reset to initial values.
     */
    const handleClear = () => {
        dispatch(clearPasswordResetRequestState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            {/* Step 4: Form title */}
            <h2>Password Reset Request</h2>

            {/* Step 5: Form for entering email */}
            <form onSubmit={handleSubmit}>
                {/* Step 5a: Email input */}
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    required
                />

                {/* Step 5b: Submit button */}
                <button type="submit" disabled={loading}>
                    {loading ? "Requesting..." : "Request Password Reset"}
                </button>
            </form>

            {/* Step 6: Display error if request failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Step 7: Display success message if request succeeded */}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            {/* Step 8: Clear button to reset form and messages */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export PasswordResetRequestForm component for use in page
export default PasswordResetRequestForm;
