// ---------------------------- External Imports ----------------------------
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

// Type-only imports for Redux
import type { TypedUseSelectorHook } from "react-redux";
import type { RootState, AppDispatch } from "../../store/store";

// ---------------------------- Internal Imports ----------------------------
import {
    requestPasswordReset,
    clearPasswordResetRequestState,
} from "./password_reset_request_slice";

// ---------------------------- Typed Selector Hook ----------------------------
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- PasswordResetRequestForm Component ----------------------------
const PasswordResetRequestForm: React.FC = () => {
    // ---------------------------- Local State ----------------------------
    const [email, setEmail] = useState("");

    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.passwordResetRequest
    );

    // ---------------------------- Event Handlers ----------------------------
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Dispatch password reset request thunk with email
        dispatch(requestPasswordReset({ email }));
    };

    const handleClear = () => {
        dispatch(clearPasswordResetRequestState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            <h2>Password Reset Request</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? "Requesting..." : "Request Password Reset"}
                </button>
            </form>

            {/* Display error if request failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if request succeeded */}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default PasswordResetRequestForm;
