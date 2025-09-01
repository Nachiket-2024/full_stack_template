// ---------------------------- External Imports ----------------------------
// Import React and hooks for component state and lifecycle
import React, { useEffect, useState } from "react";

// Import Navigate for redirecting unauthenticated users
import { Navigate } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------
// Import app settings (e.g., API base URL)
import settings from "../core/settings";

// ---------------------------- ProtectedRoute Component ----------------------------
// Define props for ProtectedRoute, expects children components
interface ProtectedRouteProps {
    children: React.ReactNode;
}

// ProtectedRoute component ensures only authenticated users can access children
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    // State to track whether the user is authenticated
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

    // Check authentication status when component mounts
    useEffect(() => {
        const checkAuth = async () => {
            try {
                // Send request to API to verify user authentication
                const res = await fetch(`${settings.apiBaseUrl}/auth/me`, {
                    credentials: "include", // Send HTTP-only cookies for auth
                });

                // Set auth state based on response status
                setIsAuthenticated(res.status === 200);
            } catch {
                // If request fails, mark as unauthenticated
                setIsAuthenticated(false);
            }
        };

        // Trigger the auth check
        checkAuth();
    }, []);

    // While auth is being verified, render nothing
    if (isAuthenticated === null) return null;

    // Redirect to login page if user is not authenticated
    if (!isAuthenticated) return <Navigate to="/login" replace />;

    // Render children components if authenticated
    return <>{children}</>;
};

// ---------------------------- Export ----------------------------
// Export ProtectedRoute component as default
export default ProtectedRoute;
