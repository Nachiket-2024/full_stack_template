// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX and functional components
import React from "react";

// Import Chakra UI components for layout and styling
import { Flex, Stack, Heading } from "@chakra-ui/react";

// ---------------------------- Internal Imports ----------------------------
// Import the SignupForm component
import SignupForm from "./SignupForm";

// ---------------------------- SignupPage Component ----------------------------
/**
 * SignupPage
 * Chakra UI-based signup page:
 * Methods:
 * 1. render - Returns a centered responsive card with heading and SignupForm
 */
const SignupPage: React.FC = () => {

    // ---------------------------- Render Method ----------------------------
    /**
     * Render the signup page with Chakra UI layout:
     * Input: None
     * Process:
     *   1. Center the card using Flex
     *   2. Use a Stack as a card container with padding, rounded corners, and shadow
     *   3. Add a heading for "Sign Up"
     *   4. Render the SignupForm inside the card
     * Output: JSX.Element representing the styled signup page
     */
    return (
        // Step 1: Flex container to center the card
        <Flex
            justify="center"     // Horizontal center
        >
            {/* Step 2: Card container */}
            <Stack
                w="1000px"
                maxW="800px"
                bg="white"           // Single card background
                p={10}               // Inner padding
                borderRadius="lg"    // Rounded corners
                boxShadow="lg"       // Shadow for elevation
                textAlign="center"   // Center content
            >
                {/* Step 3: Page heading */}
                <Heading fontSize="25px" color="teal.600">
                    Sign Up
                </Heading>

                {/* Step 4: Signup form */}
                <SignupForm />
            </Stack>
        </Flex>
    );
};

// ---------------------------- Component Export ----------------------------
// Export the component as default for routing or parent layout
export default SignupPage;