// ---------------------------- External Imports ----------------------------
// React and hooks for component state
import React, { useState } from "react";

// Redux hooks
import { useDispatch, useSelector } from "react-redux";

// Type-only import for TypedUseSelectorHook (required by verbatimModuleSyntax)
import type { TypedUseSelectorHook } from "react-redux";

// Type-only imports for store types
import type { RootState, AppDispatch } from "../../store/store";

// ---------------------------- Internal Imports ----------------------------
// Import login thunk and slice actions
import { loginUser, clearLoginState } from "./login_slice";

// ---------------------------- Typed Selector Hook ----------------------------
// Typed selector ensures Redux state is correctly typed
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- LoginForm Component ----------------------------
const LoginForm: React.FC = () => {
    // ---------------------------- Local State ----------------------------
    const [email, setEmail] = useState("");       // Email input
    const [password, setPassword] = useState(""); // Password input

    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();  // Typed dispatch
    const { loading, error, accessToken } = useAppSelector(
        (state) => state.login
    );

    // ---------------------------- Event Handlers ----------------------------
    // Handles form submission
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Dispatch login thunk with email/password payload
        dispatch(loginUser({ email, password }));
    };

    // Clears the login state manually
    const handleClear = () => {
        dispatch(clearLoginState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            <h2>Login</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    required
                />
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? "Logging in..." : "Login"}
                </button>
            </form>

            {/* Display error if login failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if login succeeded */}
            {accessToken && <p style={{ color: "green" }}>Login successful!</p>}

            {/* Clear login state */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default LoginForm;
