// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX syntax
import React from "react";

// Import typed selector hook and RootState
import { useSelector } from "react-redux";
import type { RootState } from "../store/store";

// Import LogoutButton component
import LogoutButton from "../auth/logout/LogoutButton";

// ---------------------------- DashboardPage Component ----------------------------
const DashboardPage: React.FC = () => {
    // Get refresh token from Redux login slice
    const refreshToken = useSelector((state: RootState) => state.login.refreshToken);

    return (
        <div className="flex flex-col items-center justify-center h-screen bg-gray-100 space-y-4">
            {/* Dashboard welcome message */}
            <h1 className="text-4xl font-bold">Welcome to your Dashboard</h1>

            {/* LogoutButton component only if refresh token exists */}
            {refreshToken && <LogoutButton refreshToken={refreshToken} />}
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default DashboardPage;
