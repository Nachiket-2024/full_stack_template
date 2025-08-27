// ---------------------------- External Imports ----------------------------
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------
// Auth pages
import LoginPage from "@/auth/login/LoginPage";
import SignupPage from "@/auth/signup/SignupPage";
import VerifyAccountPage from "@/auth/verify_account/VerifyAccountPage";
import PasswordResetRequestPage from "@/auth/password_reset_request/PasswordResetRequestPage";
import PasswordResetConfirmPage from "@/auth/password_reset_confirm/PasswordResetConfirmPage";

// Optional: NotFound page for unmatched routes
const NotFoundPage: React.FC = () => <h1>404 - Page Not Found</h1>;

// ---------------------------- App Component ----------------------------
const App: React.FC = () => {
  // ---------------------------- JSX Return ----------------------------
  return (
    // Wrap the app in Router to enable client-side routing
    <Router>
      <div>
        {/* App header shown on all pages */}
        <header>
          <h1>Full Stack Template - Auth Test</h1>
        </header>

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
      </div>
    </Router>
  );
};

// ---------------------------- Export ----------------------------
export default App;
