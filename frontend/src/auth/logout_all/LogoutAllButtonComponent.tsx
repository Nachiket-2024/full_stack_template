// ---------------------------- External Imports ----------------------------
// Import React for JSX/TSX syntax
import React from "react";

// ---------------------------- Props Type ----------------------------
// Define props expected by LogoutAllButtonComponent
interface LogoutAllButtonComponentProps {
    // True if logout-all request is in progress
    loading: boolean;

    // Stores error message if logout-all fails
    error: string | null;

    // Stores success message after logout-all succeeds
    successMessage: string | null;

    // Function to trigger logout all devices action
    onLogoutAll: () => void;
}

// ---------------------------- LogoutAllButtonComponent ----------------------------
// Presentational component for logout-all button UI
const LogoutAllButtonComponent: React.FC<LogoutAllButtonComponentProps> = ({
    loading,
    error,
    successMessage,
    onLogoutAll,
}) => {
    // ---------------------------- Render ----------------------------
    return (
        <div className="flex flex-col items-center space-y-2">
            {/* Logout all devices button */}
            <button
                onClick={onLogoutAll}                                // Call logout-all handler on click
                disabled={loading}                                   // Disable button while loading
                className="px-4 py-2 bg-red-600 text-white font-semibold rounded hover:bg-red-700 disabled:opacity-50"
            >
                {loading ? "Logging out all..." : "Logout All Devices"}
            </button>

            {/* Display error message if present */}
            {error && <p className="text-red-500">{error}</p>}

            {/* Display success message if present */}
            {successMessage && <p className="text-green-500">{successMessage}</p>}
        </div>
    );
};

// ---------------------------- Export ----------------------------
// Export LogoutAllButtonComponent for use in container
export default LogoutAllButtonComponent;
