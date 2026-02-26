// ---------------------------- External Imports ----------------------------
// Import React for component logic and lifecycle management
import React, { useEffect } from "react";

// Import Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Type-only import to create a typed selector hook for TypeScript safety
import type { TypedUseSelectorHook } from "react-redux";

// Import Chakra UI components for consistent layout and design
import { Stack, Button, Text, Spinner } from "@chakra-ui/react";

// ---------------------------- Internal Imports ----------------------------
// Import application-level types for Redux store and dispatch
import type { RootState, AppDispatch } from "../../store/store";

// Import Redux slice thunks/actions for verification logic
import { verifyAccount, clearVerifyAccountState } from "./verify_account_slice";

// ---------------------------- Typed Selector Hook ----------------------------
// Create a typed selector hook for strong state typing
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- VerifyAccountButton Component ----------------------------
/**
 * VerifyAccountButton
 * Handles the account verification process and displays
 * relevant UI feedback (loading, success, error).
 *
 * Methods:
 * 1. handleVerify — dispatches verifyAccount thunk.
 * 2. useEffect — triggers onSuccess callback on verification success.
 * 3. useEffect (cleanup) — clears verification state when unmounted.
 */
interface VerifyAccountButtonProps {
  token: string;          // Verification token from URL
  email: string;          // Associated email address
  onSuccess?: () => void; // Optional callback after successful verification
}

const VerifyAccountButton: React.FC<VerifyAccountButtonProps> = ({ token, email, onSuccess }) => {

  // ---------------------------- Redux ----------------------------
  const dispatch = useDispatch<AppDispatch>();                           // Typed Redux dispatcher
  const { loading, error, successMessage } = useAppSelector(
    (state) => state.verifyAccount
  );                                                                     // Extract verification slice state

  // ---------------------------- Effects ----------------------------
  /**
   * onSuccess trigger:
   * Input: successMessage and optional onSuccess callback
   * Process:
   *   1. Watch for changes in successMessage.
   *   2. If verification succeeded and callback exists, invoke it.
   * Output: Executes redirect or follow-up action after success.
   */
  useEffect(() => {
    if (successMessage && onSuccess) onSuccess(); // Step 1
  }, [successMessage, onSuccess]);

  /**
   * Cleanup effect:
   * Clears Redux slice when component unmounts,
   * ensuring old success/error messages don’t persist
   * if the user revisits this page.
   */
  useEffect(() => {
    return () => {
      dispatch(clearVerifyAccountState()); // Step 1: Clean slice on unmount
    };
  }, [dispatch]);

  // ---------------------------- Event Handlers ----------------------------
  /**
   * handleVerify
   * Input: none
   * Process:
   *   1. Dispatch verifyAccount thunk with provided token and email.
   * Output: Updates loading/error/success state in Redux.
   */
  const handleVerify = () => {
    dispatch(verifyAccount({ token, email })); // Step 1
  };

  // ---------------------------- Render ----------------------------
  /**
   * Input: Redux state (loading, error, successMessage)
   * Process:
   *   1. Display primary "Verify Account" button with spinner while loading.
   *   2. Show contextual messages for success or failure.
   * Output: Chakra-styled interactive UI block.
   */
  return (
    <Stack align="center" w="full">
      {/* Verify Account Button */}
      <Button
        onClick={handleVerify}
        bg="teal.600"
        _hover={{ bg: "teal.700" }}
        color="white"
        w="60%"
      >
        {loading ? (
          <>
            <Spinner size="sm" mr={2} /> Verifying...
          </>
        ) : (
          "Verify Account"
        )}
      </Button>

      {/* Error Message */}
      {error && (
        <Text fontSize="sm" color="red.500">
          {error}
        </Text>
      )}

      {/* Success Message */}
      {successMessage && (
        <Text fontSize="sm" color="green.500" fontWeight="medium">
          {successMessage}
        </Text>
      )}
    </Stack>
  );
};

// ---------------------------- Export ----------------------------
// Export component for use within verification page or elsewhere
export default VerifyAccountButton;