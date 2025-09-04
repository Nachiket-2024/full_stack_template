// ---------------------------- External Imports ----------------------------
// Import React to use JSX/TSX syntax in component
import React from "react";

// ---------------------------- Props Type ----------------------------
// Define props that LogoutButtonComponent expects from its container
interface LogoutButtonComponentProps {
    loading: boolean;                   // Indicates if the logout request is in progress
    error: string | null;               // Stores error message if any
    successMessage: string | null;      // Stores success message if any
    onLogout: () => void;               // Function to trigger logout
}

// ---------------------------- LogoutButtonComponent ----------------------------
// Presentational component for logout button UI
const LogoutButtonComponent: React.FC<LogoutButtonComponentProps> = ({
    loading,
    error,
    successMessage,
    onLogout,
}) => {
    return (
        <div className="flex flex-col items-center space-y-2">
            {/* Logout button */}
            <button
                onClick={onLogout}                                     // Trigger logout handler on click
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
// Export LogoutButtonComponent as default
export default LogoutButtonComponent;
