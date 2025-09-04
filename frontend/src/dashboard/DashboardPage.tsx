// ---------------------------- External Imports ----------------------------
// Import React to use JSX/TSX syntax in component
import React from "react";

// Import LogoutButton container components for single-device and all-device logout
import LogoutButton from "../auth/logout/LogoutButton";
import LogoutAllButton from "../auth/logout_all/LogoutAllButton";

// ---------------------------- DashboardPage Component ----------------------------
// Dashboard page displaying welcome message and logout options
const DashboardPage: React.FC = () => {
    return (
        // Only the white card container, centered text inside
        <div className="max-w-md mx-auto bg-white rounded-lg shadow p-6 space-y-4 text-center">
            {/* Dashboard welcome message */}
            <h1 className="text-2xl font-bold">Welcome to your Dashboard</h1>

            {/* Logout current device button */}
            <LogoutButton />

            {/* Logout all devices button */}
            <LogoutAllButton />
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export DashboardPage component as default
export default DashboardPage;
