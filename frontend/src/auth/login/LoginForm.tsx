// ---------------------------- External Imports ----------------------------
// Import React core and hooks for local state and side effects
import React, { useState, useEffect } from "react";

// Import Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for typed useSelector hook
import type { TypedUseSelectorHook } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Type-only imports for Redux store
import type { RootState, AppDispatch } from "../../store/store";

// Import login thunk and slice actions
import { loginUser, clearLoginState } from "./login_slice";

// ---------------------------- Props Interface ----------------------------
// Props interface for LoginForm component
interface LoginFormProps {
    onSuccess?: () => void; // Optional callback after successful login
    onAttempt?: () => void; // Optional callback triggered when a login attempt starts
}

// ---------------------------- Typed Selector Hook ----------------------------
// Create typed selector hook for TypeScript
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- LoginForm Component ----------------------------
/**
 * LoginForm
 * High-level component responsible for:
 * 1. Rendering email/password inputs
 * 2. Dispatching login thunk
 * 3. Handling success/failure messages
 * 4. Clearing form and Redux login state
 */
const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onAttempt }) => {
    // ---------------------------- Local State ----------------------------
    const [email, setEmail] = useState("");       // Step 1: Email input
    const [password, setPassword] = useState(""); // Step 2: Password input

    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>(); // Step 3: Typed dispatch
    const { loading, error, isAuthenticated } = useAppSelector(
        (state) => state.login // Step 4: Extract login slice
    );

    // ---------------------------- Effect: redirect on success ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Run effect when isAuthenticated changes
     *   2. Call onSuccess callback if login succeeded
     * Output: Redirects or triggers post-login action
     */
    useEffect(() => {
        if (isAuthenticated && onSuccess) {
            onSuccess();
        }
    }, [isAuthenticated, onSuccess]);

    // ---------------------------- Event Handlers ----------------------------
    /**
     * handleSubmit
     * Input: Form submit event
     * Process:
     *   0. Trigger onAttempt callback if provided
     *   1. Prevent default form submission
     *   2. Dispatch login thunk with email/password
     * Output: Updates Redux state (loading, error, isAuthenticated)
     */
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onAttempt?.(); // Step 0: notify parent about login attempt
        dispatch(loginUser({ email, password }));
    };

    /**
     * handleClear
     * Input: None
     * Process:
     *   1. Clear Redux login state
     *   2. Clear local email and password inputs
     * Output: Form and Redux slice reset
     */
    const handleClear = () => {
        dispatch(clearLoginState());
        setEmail("");
        setPassword("");
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            {/* Step 1: Form title */}
            <h2>Login</h2>

            {/* Step 2: Login form */}
            <form onSubmit={handleSubmit}>
                {/* Step 2a: Email input */}
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    required
                />

                {/* Step 2b: Password input */}
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                    required
                />

                {/* Step 2c: Submit button */}
                <button type="submit" disabled={loading}>
                    {loading ? "Logging in..." : "Login"}
                </button>
            </form>

            {/* Step 3: Display error message */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Step 4: Display success message */}
            {isAuthenticated && <p style={{ color: "green" }}>Login successful!</p>}

            {/* Step 5: Clear button */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export LoginForm component for reuse
export default LoginForm;
