// ---------------------------- External Imports ----------------------------
// Import React to use JSX/TSX syntax in component
import React, { useEffect } from "react";

// Import Redux hooks
import { useDispatch } from "react-redux";

// Import LogoutButton container components for single-device and all-device logout
import LogoutButton from "../auth/logout/LogoutButton";
import LogoutAllButton from "../auth/logout_all/LogoutAllButton";

// Import actions to clear previous logout messages
import { clearLogoutState } from "../auth/logout/logout_slice";
import { clearLogoutAllState } from "../auth/logout_all/logout_all_slice";

// ---------------------------- DashboardPage Component ----------------------------
// Functional component for user dashboard
// Methods:
// 1. render - Returns the dashboard UI including welcome message and logout buttons
const DashboardPage: React.FC = () => {
    const dispatch = useDispatch();

    // ---------------------------- Effects ----------------------------
    // Clear old logout messages when dashboard mounts
    useEffect(() => {
        dispatch(clearLogoutState());
        dispatch(clearLogoutAllState());
    }, [dispatch]);

    // ---------------------------- Render ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Render container div with styling (white card, centered, padding, shadow)
     *   2. Display heading with welcome message
     *   3. Render LogoutButton for current device
     *   4. Render LogoutAllButton for all devices
     * Output: JSX.Element representing the dashboard page
     */
    return (
        // Step 1: Container div with styling
        <div className="max-w-md mx-auto bg-white rounded-lg shadow p-6 space-y-4 text-center">

            {/* Step 2: Dashboard welcome message */}
            <h1 className="text-2xl font-bold">Welcome to your Dashboard</h1>

            {/* Step 3: Logout current device button */}
            <LogoutButton />

            {/* Step 4: Logout all devices button */}
            <LogoutAllButton />
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export DashboardPage component as default for routing
export default DashboardPage;
