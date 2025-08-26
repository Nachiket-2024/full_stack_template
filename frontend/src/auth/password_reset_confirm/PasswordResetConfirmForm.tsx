// ---------------------------- External Imports ----------------------------
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

// Type-only imports for Redux
import type { TypedUseSelectorHook } from "react-redux";
import type { RootState, AppDispatch } from "@/store/store";

// ---------------------------- Internal Imports ----------------------------
import {
    confirmPasswordReset,
    clearPasswordResetConfirmState,
} from "./password_reset_confirm_slice";

// ---------------------------- Typed Selector Hook ----------------------------
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- PasswordResetConfirmForm Component ----------------------------
const PasswordResetConfirmForm: React.FC = () => {
    // ---------------------------- Local State ----------------------------
    const [token, setToken] = useState("");
    const [newPassword, setNewPassword] = useState("");

    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.passwordResetConfirm
    );

    // ---------------------------- Event Handlers ----------------------------
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Dispatch confirm password reset thunk with token and new password
        dispatch(confirmPasswordReset({ token, new_password: newPassword }));
    };

    const handleClear = () => {
        dispatch(clearPasswordResetConfirmState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            <h2>Reset Password</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    placeholder="Token from email"
                    required
                />
                <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="New Password"
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? "Resetting..." : "Reset Password"}
                </button>
            </form>

            {/* Display error if reset failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if reset succeeded */}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default PasswordResetConfirmForm;
