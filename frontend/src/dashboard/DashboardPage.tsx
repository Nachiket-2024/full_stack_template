// ---------------------------- External Imports ----------------------------
// Import React to use JSX/TSX syntax in component
import React, { useEffect } from "react";

// Import Redux hooks
import { useDispatch } from "react-redux";

// Import Chakra UI components for layout and styling
import { Box, Heading, Stack, Container } from "@chakra-ui/react";

// Import LogoutButton container components for single-device and all-device logout
import LogoutButton from "../auth/logout/LogoutButton";
import LogoutAllButton from "../auth/logout_all/LogoutAllButton";

// Import actions to clear previous logout messages
import { clearLogoutState } from "../auth/logout/logout_slice";
import { clearLogoutAllState } from "../auth/logout_all/logout_all_slice";

// ---------------------------- DashboardPage Component ----------------------------
/**
 * DashboardPage
 * A Chakra UI-based user dashboard responsible for:
 * 1. Rendering a responsive centered container
 * 2. Displaying a welcome message
 * 3. Providing logout buttons for current and all sessions
 */
const DashboardPage: React.FC = () => {
    const dispatch = useDispatch();

    // ---------------------------- Effects ----------------------------
    // Clear old logout messages when dashboard mounts
    useEffect(() => {
        dispatch(clearLogoutState());
        dispatch(clearLogoutAllState());
    }, [dispatch]);

    // Background color
    const cardBg = "white";
    const textColor = "gray.700";

    // ---------------------------- Render ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Create a centered Chakra Container
     *   2. Use a Box as a card with padding, rounded corners, and shadow
     *   3. Display heading text
     *   4. Render LogoutButton and LogoutAllButton components
     * Output: Chakra-styled JSX.Element representing the dashboard
     */
    return (
        <Container maxW="md" py={10}>
            {/* Step 1: Dashboard card */}
            <Box
                bg={cardBg}                          // Dynamic background
                color={textColor}                    // Text color for readability
                p={8}                                // Inner padding
                rounded="xl"                         // Rounded corners
                shadow="xl"                          // Elevation shadow
                textAlign="center"                   // Center content alignment
            >
                {/* Step 2: Welcome message */}
                <Heading as="h1" fontSize="22px" mb={6} color="teal.600" >
                    Welcome to your Dashboard
                </Heading>

                {/* Step 3: Stack for spacing between buttons */}
                <Stack>
                    <LogoutButton />       {/* Logout current device */}
                    <LogoutAllButton />    {/* Logout all devices */}
                </Stack>
            </Box>
        </Container>
    );
};

// ---------------------------- Export ----------------------------
// Export DashboardPage component as default for routing
export default DashboardPage;