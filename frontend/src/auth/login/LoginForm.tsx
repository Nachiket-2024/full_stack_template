// ---------------------------- External Imports ----------------------------
// Import React core and hooks for local state and side effects
import React, { useState, useEffect } from "react";

// Import Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import for typed useSelector hook
import type { TypedUseSelectorHook } from "react-redux";

// Import Chakra UI components for inputs and buttons
import { Input, Button, Stack, Text } from "@chakra-ui/react";

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
    const { error, isAuthenticated } = useAppSelector(
        (state) => state.login // Step 4: Extract login slice
    );

    // ---------------------------- Effect: redirect on success ----------------------------
    useEffect(() => {
        if (isAuthenticated && onSuccess) {
            onSuccess();
        }
    }, [isAuthenticated, onSuccess]);

    // ---------------------------- Event Handlers ----------------------------
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onAttempt?.(); // Step 0: notify parent about login attempt
        dispatch(loginUser({ email, password }));
    };

    const handleClear = () => {
        dispatch(clearLoginState());
        setEmail("");
        setPassword("");
    };

    // ---------------------------- Render ----------------------------
    return (
        <Stack w="full">
            {/* Step 1: Email input */}
            <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                required
            />

            {/* Step 2: Password input */}
            <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                required
            />

            {/* Step 3: Submit button styled with Chakra */}
            <Button
                type="submit"
                bg="teal.600"
                _hover={{ bg: "teal.700" }}
                color="white"
                size="lg"
                w="full"
                onClick={handleSubmit}
            >
                Login
            </Button>

            {/* Step 4: Clear button styled with Chakra */}
            <Button
                type="button"
                bg="gray.300"
                _hover={{ bg: "gray.400" }}
                color="gray.700"
                size="lg"
                w="full"
                onClick={handleClear}
            >
                Clear
            </Button>

            {/* Step 5: Display error message */}
            {error && <Text color="red.500">{error}</Text>}

            {/* Step 6: Display success message */}
            {isAuthenticated && <Text color="green.500">Login successful!</Text>}
        </Stack>
    );
};

// ---------------------------- Export ----------------------------
// Export LoginForm component for reuse
export default LoginForm;