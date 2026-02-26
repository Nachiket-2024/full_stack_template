// ---------------------------- External Imports ----------------------------
// Import React for component rendering
import React from "react";

// Import React Router hooks for handling URL parameters and navigation
import { useSearchParams, useNavigate } from "react-router-dom";

// Import Chakra UI components for layout and visual design
import { Box, Text, VStack, Container } from "@chakra-ui/react";

// ---------------------------- Internal Imports ----------------------------
// Import the VerifyAccountButton component
import VerifyAccountButton from "./VerifyAccountButton";

// ---------------------------- VerifyAccountPage Component ----------------------------
/**
 * VerifyAccountPage
 * Displays a Chakra-styled card layout containing the
 * VerifyAccountButton component.
 *
 * Methods:
 * 1. handleSuccessRedirect — navigates to login page after success.
 */
const VerifyAccountPage: React.FC = () => {

  // ---------------------------- Hooks ----------------------------
  /**
   * Input: none
   * Process:
   *   1. Extract token and email from URL query parameters.
   *   2. Prepare navigation function for redirect.
   * Output:
   *   1. Token and email values.
   *   2. Navigation method.
   */
  const [searchParams] = useSearchParams();  // Step 1: Read URL params
  const navigate = useNavigate();            // Step 2: Setup router navigation

  // Step 3: Extract token and email with fallbacks
  const token = searchParams.get("token") || "";
  const email = searchParams.get("email") || "";

  // ---------------------------- Handlers ----------------------------
  /**
   * handleSuccessRedirect
   * Input: none
   * Process:
   *   1. Redirects user to "/login" upon successful verification.
   *   2. Replaces current history entry to prevent back navigation.
   * Output: User navigated to login screen.
   */
  const handleSuccessRedirect = () => {
    navigate("/login", { replace: true });
  };

  // ---------------------------- Render ----------------------------
  /**
   * Input: token, email, handleSuccessRedirect
   * Process:
   *   1. Render a centered card with teal heading and short description.
   *   2. Embed VerifyAccountButton component for verification logic.
   * Output: Fully responsive, teal-themed verification page.
   */
  return (
    <Container
      maxW="lg"
    >
      {/* Outer Card Container */}
      <Box
        w="full"
        p={8}
        borderWidth="1px"
        borderRadius="lg"
        boxShadow="lg"
        textAlign="center"
      >
        {/* Page Heading */}
        <Text
          fontSize="2xl"
          fontWeight="bold"
          color="teal.600"
          mb={6}
        >
          Verify Your Account
        </Text>

        {/* Instructional Text */}
        <Text fontSize="md" color="gray.600" mb={6}>
          Click the button below to verify your account and activate access.
        </Text>

        {/* Verification Button Block */}
        <VStack>
          <VerifyAccountButton
            token={token}
            email={email}
            onSuccess={handleSuccessRedirect}
          />
        </VStack>
      </Box>
    </Container>
  );
};

// ---------------------------- Export ----------------------------
// Export page component for routing integration
export default VerifyAccountPage;