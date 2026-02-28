// ---------------------------- External Imports ----------------------------
// Import React core for JSX/TSX syntax
import React from "react";

// Import Chakra UI components for layout and styling
import { Button, Text, Stack } from "@chakra-ui/react";

// ---------------------------- Props Interface ----------------------------
// Define props expected by LogoutAllButtonComponent
interface LogoutAllButtonComponentProps {
    loading: boolean;              // True if logout-all request is in progress
    error: string | null;          // Stores error message if logout-all fails
    successMessage: string | null; // Stores success message after logout-all succeeds
    onLogoutAll: () => void;       // Function to trigger logout-all action
}

// ---------------------------- LogoutAllButtonComponent ----------------------------
/**
 * LogoutAllButtonComponent
 * High-level presentational component responsible for:
 * 1. Rendering Chakra-styled "Logout All Devices" button
 * 2. Handling loading state display
 * 3. Displaying success or error messages
 */
const LogoutAllButtonComponent: React.FC<LogoutAllButtonComponentProps> = ({
    error,
    successMessage,
    onLogoutAll,
}) => {
    // ---------------------------- Render ----------------------------
    return (
        <Stack
            align="center"      // Center-align button and messages
        >
            {/* Step 1: Logout all devices button styled with Chakra UI */}
            <Button
                onClick={onLogoutAll}                     // Trigger logout-all handler
                loadingText="Logging out all..."          // Text while loading
                bg="red.600"                              // Chakra danger color
                _hover={{ bg: "red.700" }}                // Darker hover effect
                color="white"                             // White text for contrast
                size="lg"                                 // Large button for emphasis
                w="160px"
                h="40px"
            >
                Logout All Devices
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
// Export LogoutAllButtonComponent for reuse
export default LogoutAllButtonComponent;