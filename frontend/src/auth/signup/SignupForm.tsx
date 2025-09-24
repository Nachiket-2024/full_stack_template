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
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [localError, setLocalError] = useState("");
    const [passwordStrength, setPasswordStrength] = useState<"Weak" | "Medium" | "Strong" | "">("");

    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();
    const { loading, error, successMessage } = useAppSelector((state) => state.signup);

    // ---------------------------- Password Validation ----------------------------
    const checkRules = (pwd: string) => {
        return {
            lengthRule: pwd.length >= 8,
            upperRule: /[A-Z]/.test(pwd),
            numberRule: /[0-9]/.test(pwd),
            specialRule: /[!@#$%^&*(),.?":{}|<>]/.test(pwd),
        };
    };

    const evaluatePasswordStrength = (pwd: string): "Weak" | "Medium" | "Strong" | "" => {
        if (!pwd) return "";
        const { lengthRule, upperRule, numberRule, specialRule } = checkRules(pwd);
        const passedRules = [lengthRule, upperRule, numberRule, specialRule].filter(Boolean).length;

        if (passedRules <= 2) return "Weak";
        if (passedRules === 3) return "Medium";
        return "Strong";
    };

    const validatePassword = (pwd: string): string | null => {
        const { lengthRule, upperRule, numberRule, specialRule } = checkRules(pwd);
        if (!lengthRule) return "Password must be at least 8 characters long";
        if (!upperRule) return "Password must contain at least one uppercase letter";
        if (!numberRule) return "Password must contain at least one number";
        if (!specialRule) return "Password must contain at least one special character";
        return null;
    };

    // ---------------------------- Event Handlers ----------------------------
    const handlePasswordChange = (value: string) => {
        setPassword(value);
        setPasswordStrength(evaluatePasswordStrength(value));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Step 1: Validate password strength
        const passwordError = validatePassword(password);
        if (passwordError) {
            setLocalError(passwordError);
            return;
        }

        // Step 2: Validate confirm password
        if (password !== confirmPassword) {
            setLocalError("Passwords do not match");
            return;
        }

        // Step 3: Clear local errors
        setLocalError("");

        // Step 4: Dispatch signup action with form data
        dispatch(signupUser({ name, email, password }));
    };

    const handleClear = () => {
        setName("");
        setEmail("");
        setPassword("");
        setConfirmPassword("");
        setLocalError("");
        setPasswordStrength("");
        dispatch(clearSignupState());
    };

    // ---------------------------- Render ----------------------------
    const rules = checkRules(password);

    return (
        <div>
            {/* Form title */}
            <h2>Signup</h2>

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
                    onChange={(e) => handlePasswordChange(e.target.value)}
                    placeholder="Password"
                    required
                />

                {/* Password strength meter */}
                {passwordStrength && (
                    <p
                        style={{
                            color:
                                passwordStrength === "Weak"
                                    ? "red"
                                    : passwordStrength === "Medium"
                                        ? "orange"
                                        : "green",
                            fontWeight: "bold",
                        }}
                    >
                        Strength: {passwordStrength}
                    </p>
                )}

                {/* Password checklist */}
                <ul style={{ fontSize: "0.9rem", listStyle: "none", paddingLeft: 0 }}>
                    <li style={{ color: rules.lengthRule ? "green" : "red" }}>
                        {rules.lengthRule ? "✓" : "✗"} At least 8 characters
                    </li>
                    <li style={{ color: rules.upperRule ? "green" : "red" }}>
                        {rules.upperRule ? "✓" : "✗"} At least one uppercase letter
                    </li>
                    <li style={{ color: rules.numberRule ? "green" : "red" }}>
                        {rules.numberRule ? "✓" : "✗"} At least one number
                    </li>
                    <li style={{ color: rules.specialRule ? "green" : "red" }}>
                        {rules.specialRule ? "✓" : "✗"} At least one special character
                    </li>
                </ul>

                {/* Confirm Password input */}
                <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm Password"
                    required
                />

                {/* Submit button */}
                <button type="submit" disabled={loading}>
                    {loading ? "Signing up..." : "Signup"}
                </button>
            </form>

            {/* Display client-side validation error */}
            {localError && <p style={{ color: "red" }}>{localError}</p>}

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
export default SignupForm;
