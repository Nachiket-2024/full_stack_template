// ---------------------------- External Imports ----------------------------
import React from "react";
import { useDispatch, useSelector } from "react-redux";

// Type-only imports for Redux
import type { TypedUseSelectorHook } from "react-redux";
import type { RootState, AppDispatch } from "@/store/store";

// ---------------------------- Internal Imports ----------------------------
import { verifyAccount, clearVerifyAccountState } from "./verify_account_slice";

// ---------------------------- Typed Selector Hook ----------------------------
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ---------------------------- VerifyAccountButton Component ----------------------------
interface VerifyAccountButtonProps {
    token: string;
    email: string;
}

const VerifyAccountButton: React.FC<VerifyAccountButtonProps> = ({ token, email }) => {
    // ---------------------------- Redux ----------------------------
    const dispatch = useDispatch<AppDispatch>();
    const { loading, error, successMessage } = useAppSelector((state) => state.verifyAccount);

    // ---------------------------- Event Handlers ----------------------------
    const handleVerify = () => {
        dispatch(verifyAccount({ token, email }));
    };

    const handleClear = () => {
        dispatch(clearVerifyAccountState());
    };

    // ---------------------------- Render ----------------------------
    return (
        <div>
            <button onClick={handleVerify} disabled={loading}>
                {loading ? "Verifying..." : "Verify Account"}
            </button>

            {error && <p style={{ color: "red" }}>{error}</p>}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            <button onClick={handleClear}>Clear</button>
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default VerifyAccountButton;
