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

// Import actions from password reset confirm slice
import { confirmPasswordReset, clearPasswordResetConfirmState } from "./password_reset_confirm_slice";

// ---------------------------- Typed Selector Hook ----------------------------
// Create typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- PasswordResetConfirmForm Component ----------------------------
// Component to handle password reset confirmation
const PasswordResetConfirmForm: React.FC = () => {
    // ---------------------------- Local State ----------------------------
    // State for token input from email
    const [token, setToken] = useState("");
    // State for new password input
    const [newPassword, setNewPassword] = useState("");

    // ---------------------------- Redux ----------------------------
    // Get typed dispatch function
    const dispatch = useDispatch<AppDispatch>();
    // Get password reset confirm state from Redux store
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.passwordResetConfirm
    );

    // ---------------------------- Event Handlers ----------------------------
    // Handle form submission to confirm password reset
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        dispatch(confirmPasswordReset({ token, new_password: newPassword }));
    };

    // Clear form state and messages
    const handleClear = () => {
        dispatch(clearPasswordResetConfirmState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            {/* Form title */}
            <h2>Reset Password</h2>

            {/* Password reset confirmation form */}
            <form onSubmit={handleSubmit}>
                {/* Token input from email */}
                <input
                    type="text"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    placeholder="Token from email"
                    required
                />

                {/* New password input */}
                <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="New Password"
                    required
                />

                {/* Submit button */}
                <button type="submit" disabled={loading}>
                    {loading ? "Resetting..." : "Reset Password"}
                </button>
            </form>

            {/* Display error message if reset failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if reset succeeded */}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            {/* Clear button to reset form and messages */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export PasswordResetConfirmForm as default
export default PasswordResetConfirmForm;
