// ---------------------------- External Imports ----------------------------
// Import React core and hooks
import React, { useEffect } from "react";

// Import React Router components for routing
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Import Redux hooks for state management
import { useDispatch } from "react-redux";

// ---------------------------- Internal Imports ----------------------------
// Import authentication-related pages
import LoginPage from "./auth/login/LoginPage";
import SignupPage from "./auth/signup/SignupPage";
import VerifyAccountPage from "./auth/verify_account/VerifyAccountPage";
import PasswordResetRequestPage from "./auth/password_reset_request/PasswordResetRequestPage";
import PasswordResetConfirmPage from "./auth/password_reset_confirm/PasswordResetConfirmPage";

// Import main application pages and route guard
import DashboardPage from "./dashboard/DashboardPage";
import ProtectedRoute from "./auth/ProtectedRoute";

// Import thunk to fetch current user session and Redux types
import { fetchCurrentUser } from "./auth/current_user/current_user_slice";
import type { AppDispatch } from "./store/store";

// ---------------------------- NotFoundPage Component ----------------------------
// Simple 404 page for unmatched routes
const NotFoundPage: React.FC = () => (
  <div className="flex items-center justify-center h-screen bg-gray-100">
    <h1 className="text-4xl text-red-600 font-semibold">404 - Page Not Found</h1>
  </div>
);

// ---------------------------- App Component ----------------------------
/**
 * App
 * High-level component responsible for routing and initializing user session
 * Methods:
 * 1. useEffect - Fetches current user session on mount
 * 2. Render - Defines routes, layout, and page components
 */
const App: React.FC = () => {

  // ---------------------------- Redux Setup ----------------------------
  // Input: None
  // Process: Setup typed dispatch for Redux
  // Output: AppDispatch function for dispatching actions
  const dispatch: AppDispatch = useDispatch();

  // ---------------------------- Effect: Fetch Current User ----------------------------
  /**
   * Input: None (runs automatically on component mount)
   * Process:
   *   1. Run effect only once on initial mount
   *   2. Dispatch thunk to fetch current user session from /auth/me
   *   3. Prevent redundant calls by guarding execution
   * Output: Updates Redux state with user info or guest status
   */
  useEffect(() => {
    // Step 1: Define guard variable to ensure one-time execution
    let initialized = false;

    // Step 2: Execute fetch only once when component mounts
    if (!initialized) {
      initialized = true; // Step 2a: Mark initialized to block reruns
      dispatch(fetchCurrentUser("AppUseEffect")); // Step 2b: Fetch current user session
    }

    // Step 3: Disable React warning about missing dependencies intentionally
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dispatch]);

  // ---------------------------- Render ----------------------------
  /**
   * Input: Redux state (current user), Router configuration
   * Process:
   *   1. Wrap app in BrowserRouter for routing
   *   2. Render header with title
   *   3. Define main content area with Routes
   *       a. Protected dashboard route at "/" and "/dashboard"
   *       b. Public authentication routes (login, signup, verify-account, password reset)
   *       c. Catch-all fallback route to NotFoundPage
   * Output: JSX.Element representing the entire application UI
   */
  return (
    <Router>
      {/* Step 1: App container */}
      <div className="min-h-screen bg-gray-50">

        {/* Step 2: Header displayed on all pages */}
        <header className="bg-blue-600 text-white p-4 shadow-md">
          <h1 className="text-3xl font-bold text-center">
            Full Stack Template - Auth Test
          </h1>
        </header>

        {/* Step 3: Main content area */}
        <main className="p-6">
          <Routes>

            {/* Step 3a: Protected dashboard route (default path) */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            {/* Step 3b: Authentication-related routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/verify-account" element={<VerifyAccountPage />} />
            <Route path="/password-reset-request" element={<PasswordResetRequestPage />} />
            <Route path="/password-reset-confirm/:token" element={<PasswordResetConfirmPage />} />

            {/* Step 3c: Explicit dashboard route */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            {/* Step 3d: Catch-all fallback route */}
            <Route path="*" element={<NotFoundPage />} />

          </Routes>
        </main>
      </div>
    </Router>
  );
};

// ---------------------------- Export ----------------------------
// Export App component as default entry point for the frontend
export default App;
