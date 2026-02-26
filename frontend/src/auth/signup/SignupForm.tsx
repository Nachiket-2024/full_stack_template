// ---------------------------- External Imports ----------------------------
// React core and state management
import React, { useState } from "react";

// Redux hooks for dispatch and typed selector
import { useDispatch, useSelector } from "react-redux";
import type { TypedUseSelectorHook } from "react-redux";

// Chakra UI components for layout, inputs, buttons, text, and boxes
import { Stack, Input, Button, Text, Box } from "@chakra-ui/react";

// Chakra UI Field components for form field composition (v3)
import { Field as ChakraField } from "@chakra-ui/react";

// ---------------------------- Internal Imports ----------------------------
// TypeScript types for Redux store and dispatch
import type { RootState, AppDispatch } from "../../store/store";

// Redux thunks/actions for signup and clearing signup state
import { signupUser, clearSignupState } from "./signup_slice";

// ---------------------------- Typed Selector Hook ----------------------------
// Strongly-typed useSelector for accessing Redux state
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- SignupForm Component ----------------------------
/**
 * SignupForm
 * Functional component for user signup using Chakra UI v3.
 * Methods:
 * 1. checkRules - Validate password against rules
 * 2. evaluatePasswordStrength - Determine password strength
 * 3. validatePassword - Return first password error
 * 4. handlePasswordChange - Update password and strength
 * 5. handleSubmit - Validate and dispatch signup
 * 6. handleClear - Reset form and Redux state
 */
const SignupForm: React.FC = () => {

    // ---------------------------- Local State ----------------------------
    const [name, setName] = useState("");                       // Name input value
    const [email, setEmail] = useState("");                     // Email input value
    const [password, setPassword] = useState("");               // Password input value
    const [confirmPassword, setConfirmPassword] = useState(""); // Confirm password input value

    const [localError, setLocalError] = useState("");           // Local validation error
    const [passwordStrength, setPasswordStrength] = useState<"Weak" | "Medium" | "Strong" | "">(""); // Strength indicator

    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();               // Typed dispatch for actions
    const { error, successMessage } = useAppSelector(state => state.signup); // Signup slice state

    // ---------------------------- Password Rules ----------------------------
    const checkRules = (pwd: string) => ({
        lengthRule: pwd.length >= 8,                                 // Rule 1: min 8 chars
        upperRule: /[A-Z]/.test(pwd),                                // Rule 2: uppercase
        numberRule: /[0-9]/.test(pwd),                               // Rule 3: number
        specialRule: /[!@#$%^&*(),.?":{}|<>]/.test(pwd),             // Rule 4: special char
    });

    const evaluatePasswordStrength = (pwd: string): "Weak" | "Medium" | "Strong" | "" => {
        if (!pwd) return ""; // Empty password
        const { lengthRule, upperRule, numberRule, specialRule } = checkRules(pwd);
        const passedRules = [lengthRule, upperRule, numberRule, specialRule].filter(Boolean).length;
        if (passedRules <= 2) return "Weak";       // Weak if 0-2 rules
        if (passedRules === 3) return "Medium";    // Medium if 3 rules
        return "Strong";                           // Strong if all 4 rules
    };

    const validatePassword = (pwd: string): string | null => {
        const { lengthRule, upperRule, numberRule, specialRule } = checkRules(pwd);
        if (!lengthRule) return "Password must be at least 8 characters long";
        if (!upperRule) return "Password must contain at least one uppercase letter";
        if (!numberRule) return "Password must contain at least one number";
        if (!specialRule) return "Password must contain at least one special character";
        return null; // Password valid
    };

    // ---------------------------- Event Handlers ----------------------------
    const handlePasswordChange = (value: string) => {
        setPassword(value);                                // Step 1: Update password
        setPasswordStrength(evaluatePasswordStrength(value)); // Step 2: Update strength
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault(); // Prevent default form submission

        const passwordError = validatePassword(password);  // Step 1: Validate password
        if (passwordError) {
            setLocalError(passwordError);                  // Step 2: Show error
            return;
        }

        if (password !== confirmPassword) {                // Step 3: Confirm password match
            setLocalError("Passwords do not match");
            return;
        }

        setLocalError("");                                 // Step 4: Clear errors

        dispatch(signupUser({ name, email, password }));   // Step 5: Dispatch signup
    };

    const handleClear = () => {
        setName(""); setEmail(""); setPassword(""); setConfirmPassword(""); // Clear inputs
        setLocalError(""); setPasswordStrength("");                           // Clear validation
        dispatch(clearSignupState());                                         // Reset Redux slice
    };

    const rules = checkRules(password); // Compute rules for checklist

    // ---------------------------- Render ----------------------------
    return (
        <Stack as="form" onSubmit={handleSubmit} w="full">
            {/* ---------------- Name & Email on one line ---------------- */}
            <Stack direction="row">
                {/* Name Field */}
                <ChakraField.Root required flex={1}>
                    <ChakraField.Label>Name</ChakraField.Label>
                    <Input
                        type="text"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        placeholder="Enter your name"
                    />
                </ChakraField.Root>

                {/* Email Field */}
                <ChakraField.Root required flex={1}>
                    <ChakraField.Label>Email</ChakraField.Label>
                    <Input
                        type="email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        placeholder="Enter your email"
                    />
                </ChakraField.Root>
            </Stack>

            {/* Password Field */}
            <ChakraField.Root required>
                <ChakraField.Label>Password</ChakraField.Label>
                <Input
                    type="password"
                    value={password}
                    onChange={e => handlePasswordChange(e.target.value)}
                    placeholder="Enter password"
                />
                {/* Password Strength Indicator */}
                {passwordStrength && (
                    <Text
                        mt={1}
                        fontSize="sm"
                        fontWeight="bold"
                        color={
                            passwordStrength === "Weak" ? "red.500" :
                            passwordStrength === "Medium" ? "orange.400" : "green.500"
                        }
                    >
                        Strength: {passwordStrength}
                    </Text>
                )}
            </ChakraField.Root>

            {/* Password Rules Checklist - 2 per line */}
            <Box 
            fontSize="15px" 
            color="gray.600" 
            textAlign="center"        // Centers text horizontally
            display="flex"            // Enables flex layout for centering
            flexDirection="column"    // Keeps the two rows stacked vertically
            alignItems="center"       // Centers the inner row stacks
            >

                <Stack direction="row">
                    <Text color={rules.lengthRule ? "green.500" : "red.500"} mr={6}>
                        • {rules.lengthRule ? "✓" : "✗"} At least 8 characters
                    </Text>
                    <Text color={rules.upperRule ? "green.500" : "red.500"}>
                        • {rules.upperRule ? "✓" : "✗"} At least one uppercase letter
                    </Text>
                </Stack>
                <Stack direction="row">
                    <Text color={rules.numberRule ? "green.500" : "red.500"} mr={6}>
                        • {rules.numberRule ? "✓" : "✗"} At least one number
                    </Text>
                    <Text color={rules.specialRule ? "green.500" : "red.500"}>
                        • {rules.specialRule ? "✓" : "✗"} At least one special character
                    </Text>
                </Stack>
            </Box>

            {/* Confirm Password Field */}
            <ChakraField.Root required>
                <ChakraField.Label>Confirm Password</ChakraField.Label>
                <Input
                    type="password"
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    placeholder="Confirm password"
                />
            </ChakraField.Root>

            {/* Error and Success Messages */}
            {localError && <Text color="red.500" fontSize="17px">{localError}</Text>}
            {error && <Text color="red.500" fontSize="17px">{error}</Text>}
            {successMessage && <Text color="green.500" fontSize="17px">{successMessage}</Text>}

            {/* Action Buttons */}
            <Stack direction="row">
                <Button type="submit" bg="teal.600" _hover={{ bg: "teal.700" }} color="white">
                    Signup
                </Button>
                <Button type="button" onClick={handleClear}
                        bg="gray.300" _hover={{ bg: "gray.400" }} color="gray.700">
                    Clear
                </Button>
            </Stack>
        </Stack>
    );
};

// ---------------------------- Export ----------------------------
// Default export of SignupForm component
export default SignupForm;