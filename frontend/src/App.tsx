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
  <div className="flex items-center justify-center h-screen bg-gray-200">
    <h1 className="text-5xl text-red-600 font-bold">404 - Page Not Found</h1>
  </div>
);

// ---------------------------- App Component ----------------------------
const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Header with shadow and center-aligned title */}
        <header className="bg-blue-700 text-white p-6 shadow-md">
          <h1 className="text-4xl font-extrabold text-center">Auth System Template</h1>
        </header>

        {/* Main content area with padding and spacing */}
        <main className="p-8 sm:p-12">
          <Routes>
            {/* Default route redirect to /login */}
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

        {/* Footer with centered text */}
        <footer className="bg-gray-700 text-white text-center p-4 mt-8">
          <p>&copy; 2025 Auth Template | All Rights Reserved</p>
        </footer>
      </div>
    </Router>
  );
};

export default App;
