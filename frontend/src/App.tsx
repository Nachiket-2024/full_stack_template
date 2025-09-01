// ---------------------------- External Imports ----------------------------
// Importing React library for JSX and component creation
import React from "react";

// Importing React Router components for routing in the app
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------
// Importing Login page component
import LoginPage from "./auth/login/LoginPage";

// Importing Signup page component
import SignupPage from "./auth/signup/SignupPage";

// Importing Verify Account page component
import VerifyAccountPage from "./auth/verify_account/VerifyAccountPage";

// Importing Password Reset Request page component
import PasswordResetRequestPage from "./auth/password_reset_request/PasswordResetRequestPage";

// Importing Password Reset Confirm page component
import PasswordResetConfirmPage from "./auth/password_reset_confirm/PasswordResetConfirmPage";

// Importing ProtectedRoute component to guard routes requiring authentication
import ProtectedRoute from "./auth/ProtectedRoute";

// Importing Dashboard page component
import DashboardPage from "./dashboard/DashboardPage";

// ---------------------------- NotFoundPage Component ----------------------------
// Component to show a 404 error when route does not match
const NotFoundPage: React.FC = () => (
  <div className="flex items-center justify-center h-screen bg-gray-100">
    {/* Display 404 error message */}
    <h1 className="text-4xl text-red-600 font-semibold">404 - Page Not Found</h1>
  </div>
);

// ---------------------------- App Component ----------------------------
// Main App component handling routing and layout
const App: React.FC = () => {
  return (
    // Wrap the app in Router for navigation
    <Router>
      <div className="min-h-screen bg-gray-50">

        {/* App header shown on all pages */}
        <header className="bg-blue-600 text-white p-4 shadow-md">
          <h1 className="text-3xl font-bold text-center">Full Stack Template - Auth Test</h1>
        </header>

        {/* Main content area */}
        <main className="p-6">
          <Routes>

            {/* Default route: go to dashboard, ProtectedRoute handles redirect if not logged in */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            {/* Auth routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/verify-account" element={<VerifyAccountPage />} />
            <Route path="/password-reset-request" element={<PasswordResetRequestPage />} />
            <Route path="/password-reset-confirm/:token" element={<PasswordResetConfirmPage />} />

            {/* Protected Dashboard route */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            {/* Fallback route for unknown paths */}
            <Route path="*" element={<NotFoundPage />} />

          </Routes>
        </main>
      </div>
    </Router>
  );
};

// ---------------------------- Export ----------------------------
// Exporting App component as default
export default App;
