// ---------------------------- External Imports ----------------------------
// React core library and hooks for component lifecycle and state management
import React, { useEffect, useState } from "react";

// Redux hook to dispatch actions to the store
import { useDispatch } from "react-redux";

// Chakra UI components for layout, styling, and responsive design
import { Box, Heading, Stack, Container, Text, Spinner, Flex } from "@chakra-ui/react";

// ---------------------------- Internal Imports ----------------------------
// Button component to log out current session
import LogoutButton from "../auth/logout/LogoutButton";

// Button component to log out all sessions
import LogoutAllButton from "../auth/logout_all/LogoutAllButton";

// Redux actions to clear logout states
import { clearLogoutState } from "../auth/logout/logout_slice";
import { clearLogoutAllState } from "../auth/logout_all/logout_all_slice";

// API function to fetch current user details
import { getCurrentUserApi } from "../api/auth_api";

// ---------------------------- DashboardPage Component ----------------------------
/**
 * DashboardPage
 * Displays the current user's information and logout options
 * Methods:
 *   1. useEffect hook to fetch current user on mount
 *   2. Conditional rendering of user info, loading spinner, or error messages
 */
const DashboardPage: React.FC = () => {
    // ---------------------------- Redux Dispatch ----------------------------
    const dispatch = useDispatch(); // Step 1: Initialize Redux dispatch

    // ---------------------------- Local State ----------------------------
    const [user, setUser] = useState<{ name: string; email: string; role: string } | null>(null); 
    // Step 2a: Store current user info
    const [loading, setLoading] = useState<boolean>(true); 
    // Step 2b: Loading indicator while fetching data
    const [error, setError] = useState<string | null>(null); 
    // Step 2c: Error message if fetching fails

    // ---------------------------- Effects ----------------------------
    /**
     * useEffect
     * Input: None
     * Process:
     *   1. Clear any previous logout states in Redux
     *   2. Define async function to fetch user info
     *       2a. Call API to get current user
     *       2b. If successful, store user data in state
     *       2c. If unsuccessful, set error message
     *       2d. Stop loading after API call
     *   3. Invoke fetch function
     * Output: Updates local state with user info or error
     */
    useEffect(() => {
        // Step 1: Clear Redux logout states
        dispatch(clearLogoutState());
        dispatch(clearLogoutAllState());

        // Step 2: Async function to fetch user info
        const fetchUser = async () => {
            try {
                // Step 2a: Call API
                const res = await getCurrentUserApi("Dashboard");

                // Step 2b: If successful, update user state
                if (res.status === 200 && res.data) {
                    setUser(res.data);
                } else {
                    // Step 2c: If API response not 200, set error
                    setError("Unable to fetch user details");
                }
            } catch (err: any) {
                // Step 2c: Catch network or API errors
                setError("Failed to load user details");
            } finally {
                // Step 2d: Stop loading indicator
                setLoading(false);
            }
        };

        // Step 3: Call async fetch function
        fetchUser();
    }, [dispatch]);

    // ---------------------------- Render ----------------------------
    /**
     * Render
     * Input: Local state (user, loading, error)
     * Process:
     *   1. Display container with white background and rounded shadow
     *   2. Show heading for dashboard
     *   3. Conditionally render:
     *       3a. Spinner if loading
     *       3b. Error message if error exists
     *       3c. User info (name, email, role) if available
     *       3d. Default message if no user data
     *   4. Logout buttons in one line
     * Output: Fully styled dashboard UI
     */
    return (
        <Container maxW="md"> {/* Step 1: Center container */}
            <Box
                bg="white"          // Step 1a: Background color
                color="gray.700"    // Step 1b: Text color
                p={8}               // Step 1c: Padding
                rounded="xl"        // Step 1d: Rounded corners
                shadow="xl"         // Step 1e: Shadow
                textAlign="center"  // Step 1f: Center text
            >
                <Heading as="h1" fontSize="22px" mb={6} color="teal.600">
                    Welcome to your Dashboard {/* Step 2: Heading */}
                </Heading>

                {/* ---------------- User Info ---------------- */}
                {loading ? (
                    <Spinner size="lg" color="teal.500" /> // Step 3a: Show spinner while loading
                ) : error ? (
                    <Text color="red.500" mb={6}>{error}</Text> // Step 3b: Show error message
                ) : user ? (
                    <Stack mb={6} align="flex-start"> {/* Step 3c: Display user info aligned left */}
                        {/* Name */}
                        <Flex align="center" justify="flex-start">
                            <Box w="30px" textAlign="center" mr={2} color="teal.600"> {/* Fixed icon width */}
                                👤
                            </Box>
                            <Text fontSize="17px" fontWeight="semibold">
                                {user.name}
                            </Text>
                        </Flex>

                        {/* Email */}
                        <Flex align="center" justify="flex-start">
                            <Box w="30px" textAlign="center" mr={2} color="blue.500"> {/* Fixed icon width */}
                                📧
                            </Box>
                            <Text fontSize="17px" color="gray.600">
                                {user.email}
                            </Text>
                        </Flex>

                        {/* Role */}
                        <Flex align="center" justify="flex-start">
                            <Box w="30px" textAlign="center" mr={2} color="purple.500"> {/* Fixed icon width */}
                                🏷️
                            </Box>
                            <Text fontSize="17px" color="purple.600" fontWeight="medium">
                                {user.role}
                            </Text>
                        </Flex>
                    </Stack>
                ) : (
                    <Text color="gray.500" mb={6}>No user data available</Text> // Step 3d: Default message
                )}

                {/* ---------------- Logout Buttons ---------------- */}
                <Flex justify="center" gap={4}> {/* Step 4: Logout buttons in one line */}
                    <LogoutButton />
                    <LogoutAllButton />
                </Flex>
            </Box>
        </Container>
    );
};

// ---------------------------- Export ----------------------------
// Export DashboardPage component as default for route rendering
export default DashboardPage;