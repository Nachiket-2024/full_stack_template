// ---------------------------- External Imports ----------------------------
// Import React and hooks for component state
import React, { useState, useEffect } from "react";

// Import Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for typed useSelector hook
import type { TypedUseSelectorHook } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Type-only imports for store types
import type { RootState, AppDispatch } from "../../store/store";

// Import login thunk and slice actions
import { loginUser, clearLoginState } from "./login_slice";

// ---------------------------- Props Interface ----------------------------
// Props for LoginForm component
interface LoginFormProps {
    onSuccess?: () => void; // Callback after successful login
}

// ---------------------------- Typed Selector Hook ----------------------------
// Create typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- LoginForm Component ----------------------------
// Component for user login form
const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
    // ---------------------------- Local State ----------------------------
    const [email, setEmail] = useState("");       // Email input
    const [password, setPassword] = useState(""); // Password input

    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();   // Typed dispatch function
    const { loading, error, accessToken } = useAppSelector((state) => state.login); // Login state

    // ---------------------------- Effect: redirect on success ----------------------------
    // Only call the onSuccess callback if provided; do not navigate by default
    useEffect(() => {
        if (accessToken && onSuccess) {
            onSuccess();
        }
    }, [accessToken, onSuccess]);

    // ---------------------------- Event Handlers ----------------------------
    // Handle form submission for login
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        dispatch(loginUser({ email, password }));
    };

    // Clear login state manually
    const handleClear = () => {
        dispatch(clearLoginState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            {/* Form title */}
            <h2>Login</h2>

            {/* Login form */}
            <form onSubmit={handleSubmit}>
                {/* Email input */}
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    required
                />

                {/* Password input */}
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                    required
                />

                {/* Submit button */}
                <button type="submit" disabled={loading}>
                    {loading ? "Logging in..." : "Login"}
                </button>
            </form>

            {/* Display error message if login failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if login succeeded */}
            {accessToken && <p style={{ color: "green" }}>Login successful!</p>}

            {/* Clear button to reset form and messages */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export LoginForm component as default
export default LoginForm;
