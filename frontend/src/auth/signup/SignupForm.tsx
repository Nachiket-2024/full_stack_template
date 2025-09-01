// ---------------------------- External Imports ----------------------------
// Import React and useState hook for component state
import React, { useState } from "react";

// Import Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for typed useSelector hook
import type { TypedUseSelectorHook } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Type-only imports for store types
import type { RootState, AppDispatch } from "../../store/store";

// Import signup thunk and slice actions
import { signupUser, clearSignupState } from "./signup_slice";

// ---------------------------- Typed Selector Hook ----------------------------
// Typed selector ensures Redux state is correctly typed
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- SignupForm Component ----------------------------
// Component for user signup form
const SignupForm: React.FC = () => {
    // ---------------------------- Local State ----------------------------
    // State for name input
    const [name, setName] = useState("");
    // State for email input
    const [email, setEmail] = useState("");
    // State for password input
    const [password, setPassword] = useState("");

    // ---------------------------- Redux ----------------------------
    // Typed dispatch function
    const dispatch = useDispatch<AppDispatch>();
    // Get signup state from Redux store
    const { loading, error, successMessage } = useAppSelector((state) => state.signup);

    // ---------------------------- Event Handlers ----------------------------
    // Handle form submission for signup
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        dispatch(signupUser({ name, email, password }));
    };

    // Clear signup state manually
    const handleClear = () => {
        dispatch(clearSignupState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            {/* Form title */}
            <h2>Signup</h2>

            {/* Signup form */}
            <form onSubmit={handleSubmit}>
                {/* Name input */}
                <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Name"
                    required
                />

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
                    {loading ? "Signing up..." : "Signup"}
                </button>
            </form>

            {/* Display error message if signup failed */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message if signup succeeded */}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            {/* Clear button to reset form and messages */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export SignupForm component as default
export default SignupForm;
