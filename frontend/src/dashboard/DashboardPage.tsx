// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX syntax
import React from "react";

// Import LogoutButton component
import LogoutButton from "../auth/logout/LogoutButton";

// ---------------------------- DashboardPage Component ----------------------------
const DashboardPage: React.FC = () => {
    return (
        <div className="flex flex-col items-center justify-center h-screen bg-gray-100 space-y-4">
            {/* Dashboard welcome message */}
            <h1 className="text-4xl font-bold">Welcome to your Dashboard</h1>

            {/* LogoutButton component */}
            <LogoutButton />
        </div>
    );
};

// ---------------------------- Export ----------------------------
export default DashboardPage;
