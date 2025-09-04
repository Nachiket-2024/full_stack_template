// ---------------------------- External Imports ----------------------------
// Import React to use JSX/TSX syntax in component
import React from "react";

// ---------------------------- Props Type ----------------------------
// Define props that LogoutAllButtonComponent expects from its container
interface LogoutAllButtonComponentProps {
    loading: boolean;                   // Indicates if the logout-all request is in progress
    error: string | null;               // Stores error message if any
    successMessage: string | null;      // Stores success message if any
    onLogoutAll: () => void;            // Function to trigger logout all devices

}

// ---------------------------- LogoutAllButtonComponent ----------------------------
// Presentational component for logout-all button UI
const LogoutAllButtonComponent: React.FC<LogoutAllButtonComponentProps> = ({
    loading,
    error,
    successMessage,
    onLogoutAll,
}) => {
    return (
        <div className="flex flex-col items-center space-y-2">
            {/* Logout all devices button */}
            <button
                onClick={onLogoutAll}                                // Trigger logout-all handler on click
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
// Export LogoutAllButtonComponent as default
export default LogoutAllButtonComponent;
