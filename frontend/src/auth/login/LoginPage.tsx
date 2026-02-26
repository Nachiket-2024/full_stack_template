// ---------------------------- External Imports ----------------------------
// Import React for JSX, hooks (state and effect)
import React, { useEffect, useState } from "react";

// Import React Router hooks/components for navigation and redirection
import { useNavigate, Link, Navigate } from "react-router-dom";

// Import Redux hooks for selecting state and dispatching actions
import { useSelector, useDispatch } from "react-redux";

// Import Chakra UI components for layout, text, stack, separators, and flexbox
import { Stack, Heading, Text, StackSeparator, Flex } from "@chakra-ui/react";

// ---------------------------- Internal Imports ----------------------------
// Import LoginForm component for standard username/password login
import LoginForm from "./LoginForm";

// Import OAuth2Button component for Google OAuth2 login
import OAuth2Button from "../oauth2/OAuth2LoginButton";

// Import TypeScript types for Redux store state and dispatch
import type { RootState, AppDispatch } from "../../store/store";

// Import action to clear stale OAuth2 user session
import { clearUserSession } from "../oauth2/oauth2_slice";

// ---------------------------- LoginPage Component ----------------------------
/**
 * LoginPage
 * Renders a user login page with:
 * 1. Standard LoginForm for username/password
 * 2. OAuth2 login button (Google)
 * 3. Redirect logic for authenticated users
 * 4. Error handling and login attempt tracking
 */
const LoginPage: React.FC = () => {
    // ---------------------------- Hooks ----------------------------
    const navigate = useNavigate();                               // Hook for navigation
    const dispatch = useDispatch<AppDispatch>();                 // Typed dispatch hook
    const { isAuthenticated, loading, error } = useSelector(     // Redux state selection
        (state: RootState) => state.oauth2
    );
    const [loginAttempted, setLoginAttempted] = useState(false); // Track if login was attempted

    // ---------------------------- Effects ----------------------------
    // Effect to clear any previous OAuth2 session when page mounts
    useEffect(() => {
        dispatch(clearUserSession());  // Step 1: Clear stale session
        setLoginAttempted(false);      // Step 2: Reset login attempt tracker
    }, [dispatch]);

    // ---------------------------- Redirect / Loading ----------------------------
    // Show loading text if login process is in progress
    if (loading) return <Text>Loading...</Text>;

    // Redirect to dashboard if already authenticated
    if (isAuthenticated) return <Navigate to="/dashboard" replace />;

    // ---------------------------- Callbacks ----------------------------
    /**
     * handleLoginSuccess
     * Input: None
     * Process:
     *   1. Reset loginAttempted state
     *   2. Navigate to dashboard page
     * Output: void
     */
    const handleLoginSuccess = () => {
        setLoginAttempted(false);                       // Step 1: Reset tracker
        navigate("/dashboard", { replace: true });      // Step 2: Redirect to dashboard
    };

    /**
     * handleLoginAttempt
     * Input: None
     * Process:
     *   1. Set loginAttempted state to true
     * Output: void
     */
    const handleLoginAttempt = () => setLoginAttempted(true); // Step 1: Track login attempt

    // ---------------------------- Render ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Wrap content in a centered Flex container
     *   2. Use a Stack as the main card with padding, background, shadow, and separator
     *   3. Display heading and description
     *   4. Show error message if login failed and attempted
     *   5. Render LoginForm with callbacks
     *   6. Render OAuth2Button with callbacks
     *   7. Show signup link for new users
     * Output: JSX.Element representing the login page
     */
    return (
        <Flex justify="center">                                      {/* Step 1: Center container */}
            <Stack
                w="450px"                                                      /* Width */
                maxW="md"                                                      /* Max width medium */
                align="center"                                                 /* Center align items */
                bg="white"                                                     /* Card background color */
                p={10}                                                         /* Padding */
                borderRadius="lg"                                              /* Rounded corners */
                boxShadow="lg"                                                 /* Card shadow */
                textAlign="center"                                             /* Center text */
                separator={<StackSeparator />}                                 /* Stack separator */
            >
                {/* Step 3: Heading */}
                <Heading size="2xl" color="teal.600">Welcome</Heading>
                <Text fontSize="md" color="gray.600">
                    Sign in to continue to your dashboard
                </Text>

                {/* Step 4: Error message if login failed */}
                {error && loginAttempted && (
                    <Text color="red.500" fontWeight="bold">{error}</Text>
                )}

                {/* Step 5: Standard login form */}
                <LoginForm
                    onSuccess={handleLoginSuccess}
                    onAttempt={handleLoginAttempt}
                />

                {/* Step 6: OAuth2 login button */}
                <OAuth2Button
                    onSuccess={handleLoginSuccess}
                    onAttempt={handleLoginAttempt}
                />

                {/* Step 7: Signup link for new users */}
                <Text fontSize="16px" color="gray.600">
                    Don’t have an account?{" "}
                    <Link to="/signup" style={{ color: "#319795", fontWeight: 600 }}>
                        Sign Up
                    </Link>
                </Text>
            </Stack>
        </Flex>
    );
};

// ---------------------------- Export ----------------------------
// Export LoginPage as default component for routing
export default LoginPage;