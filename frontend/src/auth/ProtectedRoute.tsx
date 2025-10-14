// ---------------------------- External Imports ----------------------------
// Import React for component creation and JSX support
import React from "react";

// Import Navigate for conditional redirection based on authentication
import { Navigate } from "react-router-dom";

// Import Redux hook for reading authentication state
import { useSelector } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Import RootState type for typed Redux selector
import type { RootState } from "../store/store";

// ---------------------------- ProtectedRoute Component ----------------------------
/**
 * ProtectedRoute
 * Ensures that child components are only accessible to authenticated users.
 * Redirects unauthenticated users to the login page and shows a loader while session is being verified.
 * 
 * Methods:
 *   1. renderProtectedContent - Handles conditional rendering logic
 */
interface ProtectedRouteProps {
    children: React.ReactNode; // Component(s) to render if authenticated
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {

    // ---------------------------- Redux State ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Extract authentication status and loading state from Redux
     * Output:
     *   1. isAuthenticated: boolean | null
     *   2. loading: boolean
     */
    const { isAuthenticated, loading } = useSelector(
        (state: RootState) => state.currentUser
    );

    // ---------------------------- Method: renderProtectedContent ----------------------------
    /**
     * renderProtectedContent
     * Input: None
     * Process:
     *   1. If auth check is in progress or unknown, display loader
     *   2. If user is explicitly unauthenticated, redirect to login
     *   3. If user is authenticated, render the protected children components
     * Output: JSX element representing route access decision
     */
    const renderProtectedContent = () => {
        // Step 1: Show loader if auth is unknown or loading
        if (loading || isAuthenticated === null) {
            return (
                <div className="flex items-center justify-center h-screen bg-gray-100">
                    <p className="text-lg text-gray-600">Verifying session...</p>
                </div>
            );
        }

        // Step 2: Redirect unauthenticated users to login page
        if (isAuthenticated === false) {
            return <Navigate to="/login" replace />;
        }

        // Step 3: Render protected children for authenticated users
        return <>{children}</>;
    };

    // ---------------------------- Render ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Call renderProtectedContent to determine what to display
     * Output: JSX element of loader, redirect, or protected content
     */
    return renderProtectedContent();
};

// ---------------------------- Export ----------------------------
// Export component to wrap protected routes in the app
export default ProtectedRoute;
