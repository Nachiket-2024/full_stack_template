// ---------------------------- External Imports ----------------------------
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------
// Auth pages
import LoginPage from "./auth/login/LoginPage";
import SignupPage from "./auth/signup/SignupPage";
import VerifyAccountPage from "./auth/verify_account/VerifyAccountPage";
import PasswordResetRequestPage from "./auth/password_reset_request/PasswordResetRequestPage";
import PasswordResetConfirmPage from "./auth/password_reset_confirm/PasswordResetConfirmPage";

// ---------------------------- NotFoundPage Component ----------------------------
const NotFoundPage: React.FC = () => (
  <div className="flex items-center justify-center h-screen bg-gray-100">
    <h1 className="text-4xl text-red-600 font-semibold">404 - Page Not Found</h1>
  </div>
);

// ---------------------------- App Component ----------------------------
const App: React.FC = () => {
  return (
    // Wrap the app in Router to enable client-side routing
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* App header shown on all pages */}
        <header className="bg-blue-600 text-white p-4 shadow-md">
          <h1 className="text-3xl font-bold text-center">Full Stack Template - Auth Test</h1>
        </header>

        {/* Main content area */}
        <main className="p-6">
          {/* Define all routes */}
          <Routes>
            {/* Default route: redirect to /login */}
            <Route path="/" element={<Navigate to="/login" replace />} />

            {/* Auth routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/verify-account" element={<VerifyAccountPage />} />
            <Route path="/password-reset-request" element={<PasswordResetRequestPage />} />
            <Route path="/password-reset-confirm/:token" element={<PasswordResetConfirmPage />} />

            {/* Fallback route */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

// ---------------------------- Export ----------------------------
export default App;
