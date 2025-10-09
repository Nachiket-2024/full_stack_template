// ---------------------------- External Imports ----------------------------
// React library for JSX/TSX syntax and local component state
import React, { useState } from "react";

// Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for typed useSelector hook
import type { TypedUseSelectorHook } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Type-only imports for Redux store types
import type { RootState, AppDispatch } from "../../store/store";

// Import signup thunk and slice actions
import { signupUser, clearSignupState } from "./signup_slice";

// ---------------------------- Typed Selector Hook ----------------------------
// Create a typed useSelector hook for TypeScript support
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- SignupForm Component ----------------------------
// Handles user signup form, validation, and submission
// Methods:
// 1. checkRules - Returns which password rules are satisfied
// 2. evaluatePasswordStrength - Determines password strength
// 3. validatePassword - Returns validation error if password invalid
// 4. handlePasswordChange - Updates password and strength
// 5. handleSubmit - Validates and dispatches signup action
// 6. handleClear - Resets form inputs and Redux slice
const SignupForm: React.FC = () => {

    // ---------------------------- Local State ----------------------------
    const [name, setName] = useState("");                        // Step 1a: Name input
    const [email, setEmail] = useState("");                      // Step 1b: Email input
    const [password, setPassword] = useState("");                // Step 1c: Password input
    const [confirmPassword, setConfirmPassword] = useState("");  // Step 1d: Confirm password input
    const [localError, setLocalError] = useState("");            // Step 1e: Client-side validation error
    const [passwordStrength, setPasswordStrength] = useState<"Weak" | "Medium" | "Strong" | "">(""); // Step 1f: Password strength

    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>(); // Step 2a: Typed dispatch
    const { loading, error, successMessage } = useAppSelector(
        (state) => state.signup
    ); // Step 2b: Extract signup slice state

    // ---------------------------- Password Validation ----------------------------
    /**
     * checkRules
     * Input: password string
     * Process:
     *   1. Check if password has at least 8 characters
     *   2. Check if password has at least one uppercase letter
     *   3. Check if password has at least one number
     *   4. Check if password has at least one special character
     * Output: Object indicating which rules passed
     */
    const checkRules = (pwd: string) => ({
        lengthRule: pwd.length >= 8,
        upperRule: /[A-Z]/.test(pwd),
        numberRule: /[0-9]/.test(pwd),
        specialRule: /[!@#$%^&*(),.?":{}|<>]/.test(pwd),
    });

    /**
     * evaluatePasswordStrength
     * Input: password string
     * Process:
     *   1. Count how many rules pass
     *   2. Return "Weak" if <=2 rules, "Medium" if 3 rules, "Strong" if all 4 rules
     * Output: "Weak" | "Medium" | "Strong" | "" 
     */
    const evaluatePasswordStrength = (pwd: string): "Weak" | "Medium" | "Strong" | "" => {
        if (!pwd) return "";
        const { lengthRule, upperRule, numberRule, specialRule } = checkRules(pwd);
        const passedRules = [lengthRule, upperRule, numberRule, specialRule].filter(Boolean).length;
        if (passedRules <= 2) return "Weak";
        if (passedRules === 3) return "Medium";
        return "Strong";
    };

    /**
     * validatePassword
     * Input: password string
     * Process:
     *   1. Check each rule individually
     *   2. Return corresponding error message if rule fails
     * Output: string error message or null if valid
     */
    const validatePassword = (pwd: string): string | null => {
        const { lengthRule, upperRule, numberRule, specialRule } = checkRules(pwd);
        if (!lengthRule) return "Password must be at least 8 characters long";
        if (!upperRule) return "Password must contain at least one uppercase letter";
        if (!numberRule) return "Password must contain at least one number";
        if (!specialRule) return "Password must contain at least one special character";
        return null;
    };

    // ---------------------------- Event Handlers ----------------------------
    /**
     * handlePasswordChange
     * Input: new password string
     * Process:
     *   1. Update password state
     *   2. Update password strength
     * Output: Updates local component state
     */
    const handlePasswordChange = (value: string) => {
        setPassword(value); // Step 1
        setPasswordStrength(evaluatePasswordStrength(value)); // Step 2
    };

    /**
     * handleSubmit
     * Input: form event
     * Process:
     *   1. Prevent default form submission
     *   2. Validate password rules
     *   3. Validate confirm password matches
     *   4. Clear local errors
     *   5. Dispatch signupUser action
     * Output: Dispatches signup thunk to backend if validation passes
     */
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault(); // Step 1

        // Step 2: Validate password rules
        const passwordError = validatePassword(password);
        if (passwordError) {
            setLocalError(passwordError);
            return;
        }

        // Step 3: Validate confirm password matches
        if (password !== confirmPassword) {
            setLocalError("Passwords do not match");
            return;
        }

        // Step 4: Clear any local errors
        setLocalError("");

        // Step 5: Dispatch signup action to backend
        dispatch(signupUser({ name, email, password }));
    };

    /**
     * handleClear
     * Input: None
     * Process:
     *   1. Reset all form fields
     *   2. Reset local validation error
     *   3. Reset password strength
     *   4. Clear Redux signup slice state
     * Output: Resets signup form and Redux slice
     */
    const handleClear = () => {
        setName(""); setEmail(""); setPassword(""); setConfirmPassword("");
        setLocalError(""); setPasswordStrength("");
        dispatch(clearSignupState());
    };

    // ---------------------------- Render ----------------------------
    const rules = checkRules(password); // Step 1: Compute current password rules

    return (
        <div>
            {/* Form title */}
            <h2>Signup</h2>

            <form onSubmit={handleSubmit}>
                {/* Name input */}
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" required />

                {/* Email input */}
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required />

                {/* Password input */}
                <input type="password" value={password} onChange={(e) => handlePasswordChange(e.target.value)} placeholder="Password" required />

                {/* Password strength meter */}
                {passwordStrength && (
                    <p style={{ color: passwordStrength === "Weak" ? "red" : passwordStrength === "Medium" ? "orange" : "green", fontWeight: "bold" }}>
                        Strength: {passwordStrength}
                    </p>
                )}

                {/* Password rules checklist */}
                <ul style={{ fontSize: "0.9rem", listStyle: "none", paddingLeft: 0 }}>
                    <li style={{ color: rules.lengthRule ? "green" : "red" }}>{rules.lengthRule ? "✓" : "✗"} At least 8 characters</li>
                    <li style={{ color: rules.upperRule ? "green" : "red" }}>{rules.upperRule ? "✓" : "✗"} At least one uppercase letter</li>
                    <li style={{ color: rules.numberRule ? "green" : "red" }}>{rules.numberRule ? "✓" : "✗"} At least one number</li>
                    <li style={{ color: rules.specialRule ? "green" : "red" }}>{rules.specialRule ? "✓" : "✗"} At least one special character</li>
                </ul>

                {/* Confirm Password input */}
                <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Confirm Password" required />

                {/* Submit button */}
                <button type="submit" disabled={loading}>{loading ? "Signing up..." : "Signup"}</button>
            </form>

            {/* Display local validation error */}
            {localError && <p style={{ color: "red" }}>{localError}</p>}

            {/* Display Redux error message */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Display success message */}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            {/* Clear button */}
            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export SignupForm component as default
export default SignupForm;
