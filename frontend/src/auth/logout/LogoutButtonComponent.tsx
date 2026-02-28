// ---------------------------- External Imports ----------------------------
// Import React core for JSX/TSX syntax
import React from "react";

// Import Chakra UI components for layout and styling
import { Button, Text, Stack } from "@chakra-ui/react";

// ---------------------------- Props Interface ----------------------------
// Define props expected by LogoutButtonComponent
interface LogoutButtonComponentProps {
    loading: boolean;           // True if logout request is in progress
    error: string | null;       // Stores error message if logout fails
    successMessage: string | null; // Stores success message after logout succeeds
    onLogout: () => void;       // Function to trigger logout action
}

// ---------------------------- LogoutButtonComponent ----------------------------
/**
 * LogoutButtonComponent
 * High-level presentational component responsible for:
 * 1. Rendering Chakra-styled logout button
 * 2. Handling loading state display
 * 3. Displaying success or error messages
 */
const LogoutButtonComponent: React.FC<LogoutButtonComponentProps> = ({
    error,
    successMessage,
    onLogout,
}) => {
    // ---------------------------- Render ----------------------------
    return (
        <Stack
            align="center"       // Center-align button and messages
        >
            {/* Step 1: Logout button styled with Chakra UI */}
            <Button
                onClick={onLogout}                         // Trigger logout handler
                loadingText="Logging out..."               // Text while loading
                bg="red.600"                                   // Chakra color scheme for danger actions
                _hover={{ bg: "red.700" }}
                color="white"
                size="lg"                                  // Large button for emphasis
                w="160px"
                h="40px"
            >
                Logout
            </Button>

            {/* Step 2: Display error message if present */}
            {error && (
                <Text color="red.500" fontSize="md">
                    {error}
                </Text>
            )}

            {/* Step 3: Display success message if present */}
            {successMessage && (
                <Text color="green.500" fontSize="md">
                    {successMessage}
                </Text>
            )}
        </Stack>
    );
};

// ---------------------------- Export ----------------------------
// Export LogoutButtonComponent for reuse
export default LogoutButtonComponent;