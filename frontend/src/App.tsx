// ---------------------------- External Imports ----------------------------
// Import React core and hooks for component rendering and lifecycle management
import React, { useEffect } from "react";

// Import React Router components for routing and route handling
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Import Redux hooks for state selection and dispatching actions
import { useDispatch, useSelector } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Authentication-related pages
import LoginPage from "./auth/login/LoginPage";
import SignupPage from "./auth/signup/SignupPage";
import VerifyAccountPage from "./auth/verify_account/VerifyAccountPage";
import PasswordResetRequestPage from "./auth/password_reset_request/PasswordResetRequestPage";
import PasswordResetConfirmPage from "./auth/password_reset_confirm/PasswordResetConfirmPage";

// Main dashboard page and protected route wrapper
import DashboardPage from "./dashboard/DashboardPage";
import ProtectedRoute from "./auth/ProtectedRoute";

// Thunk action to fetch current user session and Redux type definitions
import { fetchCurrentUser } from "./auth/current_user/current_user_slice";
import type { AppDispatch, RootState } from "./store/store";

// ---------------------------- NotFoundPage Component ----------------------------
// Simple 404 page displayed when a route does not match any defined routes
const NotFoundPage: React.FC = () => (
  <div className="flex items-center justify-center h-screen bg-gray-100">
    <h1 className="text-4xl text-red-600 font-semibold">404 - Page Not Found</h1>
  </div>
);

// ---------------------------- App Component ----------------------------
/**
 * App
 * High-level component responsible for routing, initializing user session,
 * and rendering protected/public pages.
 * 
 * Methods:
 *   1. useEffect - Fetches current user session on mount (only if needed)
 *   2. Conditional Render - Shows loader while session check is in progress
 *   3. Render - Defines all routes and layout
 */
const App: React.FC = () => {

  // ---------------------------- Redux Setup ----------------------------
  const dispatch: AppDispatch = useDispatch(); // Step 1: Get Redux dispatch function
  const { loading, isAuthenticated } = useSelector(
    (state: RootState) => state.currentUser // Step 2: Get auth state from Redux
  );

  // ---------------------------- Effect: Fetch Current User ----------------------------
  /**
   * Input: None (runs on component mount)
   * Process:
   *   1. Only fetch user if authentication has not been checked (isAuthenticated === null)
   *   2. Prevent redundant API calls on re-render or hot-reload
   * Output: Updates Redux state with current user info or guest status
   */
  useEffect(() => {
    if (isAuthenticated === null) {
      // Step 1: Fetch current user only once per session
      dispatch(fetchCurrentUser("AppUseEffect"));
    }
  }, [dispatch, isAuthenticated]); // Step 2: Dependency array ensures effect runs only when necessary

  // ---------------------------- Conditional Render (Session Check) ----------------------------
  /**
   * Input: Redux loading and authentication state
   * Process:
   *   1. Show loading screen if session check is in progress
   *   2. Once session check completes, render the full application
   * Output: Either a loading screen or the main app content
   */
  if (loading && isAuthenticated === null) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <p className="text-lg text-gray-600">Checking session...</p>
      </div>
    );
  }

  // ---------------------------- Render ----------------------------
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">

        {/* Application Header */}
        <header className="bg-blue-600 text-white p-4 shadow-md">
          <h1 className="text-3xl font-bold text-center">
            Full Stack Template - Auth Test
          </h1>
        </header>

        {/* Main Content Area */}
        <main className="p-6">
          <Routes>
            {/* Protected Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/verify-account" element={<VerifyAccountPage />} />
            <Route path="/password-reset-request" element={<PasswordResetRequestPage />} />
            <Route path="/password-reset-confirm/:token" element={<PasswordResetConfirmPage />} />

            {/* 404 Fallback */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

// ---------------------------- Export ----------------------------
// Export App as default for usage in main entry point
export default App;
