// ---------------------------- External Imports ----------------------------
// Import React to use JSX/TSX syntax in component
import React, { useEffect } from "react";

// Import BrowserRouter, Routes, and Route for routing
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Import Redux hooks for state and dispatch access
import { useDispatch, useSelector } from "react-redux";

// Import Chakra UI components for layout, typography, buttons, and stacks
import { Box, Flex, Heading, Text, Spinner, VStack, Button } from "@chakra-ui/react";
import type { StackProps } from "@chakra-ui/react"; // Type import for stack props

// ---------------------------- Internal Imports ----------------------------
// Import authentication pages
import LoginPage from "./auth/login/LoginPage";
import SignupPage from "./auth/signup/SignupPage";
import VerifyAccountPage from "./auth/verify_account/VerifyAccountPage";
import PasswordResetRequestPage from "./auth/password_reset_request/PasswordResetRequestPage";
import PasswordResetConfirmPage from "./auth/password_reset_confirm/PasswordResetConfirmPage";

// Import dashboard page
import DashboardPage from "./dashboard/DashboardPage";

// Import ProtectedRoute component to guard private pages
import ProtectedRoute from "./auth/ProtectedRoute";

// Import Redux action to fetch current user session
import { fetchCurrentUser } from "./auth/current_user/current_user_slice";

// Import types for Redux state and dispatch
import type { AppDispatch, RootState } from "./store/store";

// ---------------------------- NotFoundPage Component ----------------------------
// Functional component for 404 page
// Methods:
// 1. render - Returns UI for page not found including heading, message, and "Go Home" button
const NotFoundPage: React.FC = () => {
    const bg = "#f0f0f0"; // Background color for 404 page
    const textColor = "#e53e3e"; // Text color for 404 heading

    // ---------------------------- Render ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Render Flex container centered vertically and horizontally
     *   2. Render VStack to stack heading, text, and button with spacing
     *   3. Display heading "404"
     *   4. Display message "Oops! Page Not Found"
     *   5. Render Button to redirect user to home page
     * Output: JSX.Element representing 404 page
     */
    return (
        // Step 1: Flex container
        <Flex align="center" justify="center" h="100vh" bg={bg} px={4} textAlign="center">
            {/* Step 2: VStack for stacking elements */}
            <VStack {...({ spacing: 4 } as StackProps)}>
                {/* Step 3: 404 heading */}
                <Heading color={textColor} size="2xl">404</Heading>

                {/* Step 4: Message */}
                <Text fontSize="xl" fontWeight="medium">Oops! Page Not Found</Text>

                {/* Step 5: Go Home button */}
                <Button
                    colorScheme="teal"
                    size="md"
                    fontWeight="bold"
                    _hover={{ bg: "teal.600" }}
                    _active={{ bg: "teal.700" }}
                    onClick={() => window.location.href = "/"}
                >
                    Go Home
                </Button>
            </VStack>
        </Flex>
    );
};

// ---------------------------- App Component ----------------------------
// Functional component for main app layout and routing
// Methods:
// 1. render - Sets up app layout including header, footer, routing, and loading state
const App: React.FC = () => {
    const dispatch: AppDispatch = useDispatch(); // Redux dispatch
    const { loading, isAuthenticated } = useSelector(
        (state: RootState) => state.currentUser // Pull authentication info from Redux
    );

    // ---------------------------- Effects ----------------------------
    // Fetch current user session on mount if authentication status is unknown
    useEffect(() => {
        if (isAuthenticated === null) {
            dispatch(fetchCurrentUser("AppUseEffect"));
        }
    }, [dispatch, isAuthenticated]);

    // ---------------------------- Loading state ----------------------------
    if (loading && isAuthenticated === null) {
        const bg = "#f0f0f0"; // Background for loading screen

        // ---------------------------- Render ----------------------------
        /**
         * Input: None
         * Process:
         *   1. Render Flex container centered vertically and horizontally
         *   2. Display Spinner for loading
         *   3. Display text "Checking session..."
         * Output: JSX.Element showing loading state
         */
        return (
            <Flex align="center" justify="center" h="100vh" bg={bg}>
                {/* Step 2: Spinner */}
                <Spinner size="xl" color="#3182ce" />

                {/* Step 3: Loading text */}
                <Text ml={4} fontSize="lg" color="#4a5568">Checking session...</Text>
            </Flex>
        );
    }

    const headerBg = "linear-gradient(to right, #4299e1, #38b2ac)"; // Header gradient
    const mainBg = "#f0f0f0"; // Main content background

    // ---------------------------- Render ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Render Router wrapper
     *   2. Render Flex container as main column layout
     *   3. Render header with app title
     *   4. Render main content with Routes
     *   5. Render footer
     * Output: JSX.Element representing full app layout with routing
     */
    return (
        // Step 1: Router
        <Router>
            {/* Step 2: Main Flex layout */}
            <Flex direction="column" minH="100vh" bg={mainBg}>
                {/* Step 3: Header */}
                <Box bg={headerBg} py={6} shadow="md">
                    <Heading textAlign="center" color="white" fontSize="3xl">Full Stack Auth Template</Heading>
                </Box>

                {/* Step 4: Main content */}
                <Flex flex="1" direction="column" py={8}>
                    <Routes>
                        {/* Protected Routes */}
                        <Route
                            path="/"
                            element={
                                <ProtectedRoute>
                                    <Box maxW="container.lg" mx="auto">
                                        <DashboardPage />
                                    </Box>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard"
                            element={
                                <ProtectedRoute>
                                    <Box maxW="container.lg" mx="auto">
                                        <DashboardPage />
                                    </Box>
                                </ProtectedRoute>
                            }
                        />

                        {/* Public Routes */}
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/signup" element={<SignupPage />} />
                        <Route path="/verify-account" element={<VerifyAccountPage />} />
                        <Route path="/password-reset-request" element={<PasswordResetRequestPage />} />
                        <Route path="/password-reset-confirm/:token" element={<PasswordResetConfirmPage />} />

                        {/* 404 Page */}
                        <Route path="*" element={<NotFoundPage />} />
                    </Routes>
                </Flex>

                {/* Step 5: Footer */}
                <Box bg="#73D5E8" py={2.5} mt="auto" textAlign="center">
                    <Text color="#4a5568" fontSize="sm">© 2026 Full Stack Template. All rights reserved.</Text>
                </Box>
            </Flex>
        </Router>
    );
};

// ---------------------------- Export ----------------------------
// Export App component as default for routing
export default App;