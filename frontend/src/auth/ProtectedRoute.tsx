// ---------------------------- External Imports ----------------------------
// Import React for component creation
import React from "react";

// Import Navigate for conditional redirection
import { Navigate } from "react-router-dom";

// Import Redux hook for reading authentication state
import { useSelector } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Import RootState type for typed useSelector
import type { RootState } from "../store/store";

// ---------------------------- ProtectedRoute Component ----------------------------
// Component: Protects routes by verifying authentication via Redux
// Methods:
// 1. renderProtectedContent - Handles conditional rendering logic
interface ProtectedRouteProps {
    children: React.ReactNode; // The component(s) to render if user is authenticated
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {

    // ---------------------------- Redux ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Extract authentication state from Redux store
     * Output:
     *   1. isAuthenticated boolean
     *   2. loading boolean
     */
    const { isAuthenticated, loading } = useSelector(
        (state: RootState) => state.currentUser
    );

    // ---------------------------- Method: renderProtectedContent ----------------------------
    /**
     * renderProtectedContent
     * Input: None
     * Process:
     *   1. If authentication check is in progress, show loader
     *   2. If user is not authenticated, redirect to login page
     *   3. If authenticated, render protected children components
     * Output: JSX element representing route protection result
     */
    const renderProtectedContent = () => {
        // Step 1: Handle loading state — display temporary UI
        if (loading) return <div>Loading...</div>;

        // Step 2: Redirect unauthenticated users to login
        if (!isAuthenticated) return <Navigate to="/login" replace />;

        // Step 3: Render protected children
        return <>{children}</>;
    };

    // ---------------------------- Render ----------------------------
    /**
     * Input: None
     * Process:
     *   1. Call renderProtectedContent to determine what to render
     * Output: JSX.Element of loader, redirect, or protected content
     */
    return renderProtectedContent();
};

// ---------------------------- Export ----------------------------
// Export ProtectedRoute component for use in route protection
export default ProtectedRoute;
