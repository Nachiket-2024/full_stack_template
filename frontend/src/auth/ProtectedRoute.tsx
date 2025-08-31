// ---------------------------- External Imports ----------------------------
import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------
import settings from "../core/settings";

// ---------------------------- ProtectedRoute Component ----------------------------
interface ProtectedRouteProps {
    children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    // State to track auth status
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const res = await fetch(`${settings.apiBaseUrl}/auth/me`, {
                    credentials: "include", // <- send HTTP-only cookies
                });

                setIsAuthenticated(res.status === 200);
            } catch {
                setIsAuthenticated(false);
            }
        };

        checkAuth();
    }, []);

    // Show nothing while auth is being verified
    if (isAuthenticated === null) return null;

    // Redirect to login if not authenticated
    if (!isAuthenticated) return <Navigate to="/login" replace />;

    // Otherwise, render children
    return <>{children}</>;
};

export default ProtectedRoute;
