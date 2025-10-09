// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX syntax
import React from "react";

// ---------------------------- Props Type ----------------------------
// Define props expected by LogoutButtonComponent
interface LogoutButtonComponentProps {
    // True if logout request is in progress
    loading: boolean;

    // Stores error message if logout fails
    error: string | null;

    // Stores success message after logout succeeds
    successMessage: string | null;

    // Function to trigger logout action
    onLogout: () => void;
}

// ---------------------------- LogoutButtonComponent ----------------------------
// Presentational component for logout button UI
const LogoutButtonComponent: React.FC<LogoutButtonComponentProps> = ({
    loading,
    error,
    successMessage,
    onLogout,
}) => {
    // ---------------------------- Render ----------------------------
    return (
        <div className="flex flex-col items-center space-y-2">
            {/* Logout button */}
            <button
                onClick={onLogout}                                     // Call logout handler on click
                disabled={loading}                                     // Disable button while loading
                className="px-4 py-2 bg-red-600 text-white font-semibold rounded hover:bg-red-700 disabled:opacity-50"
            >
                {loading ? "Logging out..." : "Logout"}
            </button>

            {/* Display error message if present */}
            {error && <p className="text-red-500">{error}</p>}

            {/* Display success message if present */}
            {successMessage && <p className="text-green-500">{successMessage}</p>}
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export LogoutButtonComponent for use in container
export default LogoutButtonComponent;
