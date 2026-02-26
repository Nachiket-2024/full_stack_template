// ---------------------------- External Imports ----------------------------
// Import React to use JSX/TSX syntax and hooks
import React, { useEffect, useState } from "react";

// Import React Router hooks for navigation and links
import { useNavigate, Link, Navigate } from "react-router-dom";

// Import Redux hooks to access state and dispatch actions
import { useSelector, useDispatch } from "react-redux";

// Import Chakra UI components for layout, typography, buttons, stacking, and Flex container
import { Stack, Heading, Text, StackSeparator, Button, Flex } from "@chakra-ui/react";

// ---------------------------- Internal Imports ----------------------------
// Login form component handling username/password inputs
import LoginForm from "./LoginForm";

// OAuth2 login button component for external provider login
import OAuth2Button from "../oauth2/OAuth2LoginButton";

// Type definitions for Redux state and dispatch
import type { RootState, AppDispatch } from "../../store/store";

// Redux action to clear any existing user session
import { clearUserSession } from "../oauth2/oauth2_slice";

// ---------------------------- LoginPage Component ----------------------------
// Functional component for rendering the login page
// Methods:
// 1. render - Returns login UI including login form, OAuth2 button, error messages, and signup link
const LoginPage: React.FC = () => {
    const navigate = useNavigate(); // Hook to navigate programmatically
    const dispatch = useDispatch<AppDispatch>(); // Redux dispatch with typed actions
    const { isAuthenticated, loading, error } = useSelector(
        (state: RootState) => state.oauth2 // Pull authentication state from Redux
    );
    const [loginAttempted, setLoginAttempted] = useState(false); // Track if login was attempted

    // ---------------------------- Effects ----------------------------
    // Clear stale session and reset loginAttempted on component mount
    useEffect(() => {
        dispatch(clearUserSession()); // Step 1: Clear existing session
        setLoginAttempted(false); // Step 2: Reset local login attempt tracker
    }, [dispatch]);

    // ---------------------------- Redirect / Loading ----------------------------
    // Show loading state or redirect authenticated users
    if (loading) return <Text>Loading...</Text>; // Step 1: Show loading text
    if (isAuthenticated) return <Navigate to="/dashboard" replace />; // Step 2: Redirect if authenticated

    // ---------------------------- Callbacks ----------------------------
    const handleLoginSuccess = () => {
        setLoginAttempted(false); // Step 1: Reset login attempt tracker
        navigate("/dashboard", { replace: true }); // Step 2: Navigate to dashboard
    };
    const handleLoginAttempt = () => setLoginAttempted(true); // Mark login attempt

    // ---------------------------- Render ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Render Flex container to horizontally center the card
     *   2. Render Stack (white card) with heading, instructional text, error message, login form, OAuth2 button, and signup link
     *   3. Display heading "Welcome"
     *   4. Display instructional text
     *   5. Conditionally display error message if login failed
     *   6. Render LoginForm with callbacks
     *   7. OAuth2 login button with Google style
     *   8. Render signup link
     * Output: JSX.Element representing the login page
     */
    return (
        // Step 1: Flex container to center card
        <Flex w="full" justify="center">
            {/* Step 2: White card Stack */}
            <Stack
                w="full" // Full width
                maxW="md" // Max card width
                align="center" // Center children horizontally
                bg="white" // Card background
                p={10} // Padding
                borderRadius="lg" // Rounded corners
                boxShadow="lg" // Shadow for depth
                textAlign="center" // Center text alignment
                separator={<StackSeparator />} // Optional visual separator
            >
                {/* Step 3: Page title */}
                <Heading size="2xl" color="teal.600">Welcome</Heading>

                {/* Step 4: Instructional text */}
                <Text fontSize="md" color="gray.600">Sign in to continue to your dashboard</Text>

                {/* Step 5: Error message */}
                {error && loginAttempted && (
                    <Text color="red.500" fontWeight="bold">{error}</Text>
                )}

                {/* Step 6: Login form */}
                <LoginForm
                    onSuccess={handleLoginSuccess}
                    onAttempt={handleLoginAttempt}
                />

                {/* Step 7: OAuth2 login button with Google style */}
                <Button
                    w="full"
                    mt={4}
                    bg="white"                  // White background
                    color="gray.800"            // Dark text
                    border="1px solid #ddd"     // Subtle border
                    _hover={{ bg: "#e0e0e0" }}  // Darker hover effect
                    size="lg"
                    onClick={() => {
                        handleLoginAttempt(); // Mark login attempt
                        OAuth2Button({ onSuccess: handleLoginSuccess, onAttempt: handleLoginAttempt }); // Trigger OAuth2 login
                    }}
                >
                    <Flex align="center" justify="center" gap={2}>
                        {/* Inline Google "G" SVG */}
                        <svg width="20" height="20" viewBox="0 0 533.5 544.3">
                            <path fill="#4285F4" d="M533.5 278.4c0-17.5-1.5-34.4-4.3-50.7H272v95.9h146.9c-6.3 33.9-25.5 62.7-54.5 82v68h87.8c51.4-47.4 80.3-116.9 80.3-195.2z"/>
                            <path fill="#34A853" d="M272 544.3c73.7 0 135.5-24.3 180.7-66.2l-87.8-68c-24.4 16.4-55.7 26-92.9 26-71.5 0-132.2-48.1-153.9-112.7h-90.6v70.8c45.3 90 138.5 150.1 244.5 150.1z"/>
                            <path fill="#FBBC05" d="M118.3 323.2c-10.7-32-10.7-66.6 0-98.6v-70.8h-90.6c-40.2 78.7-40.2 171.1 0 249.8l90.6-70.4z"/>
                            <path fill="#EA4335" d="M272 107.7c39.8-.6 77.7 14 106.6 40.8l79.9-79.9C405.9 21 345.7-4.3 272 0 166 0 72.8 60.1 27.5 150.1l90.6 70.8C139.8 155.8 200.5 107.7 272 107.7z"/>
                        </svg>
                        <span>Sign in with Google</span>
                    </Flex>
                </Button>

                {/* Step 8: Signup link */}
                <Text fontSize="sm" color="gray.600">
                    Don’t have an account?{" "}
                    <Link to="/signup" style={{ color: "#319795", fontWeight: 600 }}>Sign Up</Link>
                </Text>
            </Stack>
        </Flex>
    );
};

// ---------------------------- Export ----------------------------
// Export LoginPage component as default for routing
export default LoginPage;