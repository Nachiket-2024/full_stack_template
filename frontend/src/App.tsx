// ---------------------------- External Imports ----------------------------
// React hooks
import React from "react";

// Import your LoginForm component
import LoginForm from "@/auth/login/LoginForm";

// ---------------------------- App Component ----------------------------
const App: React.FC = () => {
  return (
    <div>
      {/* App header */}
      <h1>Full Stack Template - Login Test</h1>

      {/* Render the login form component */}
      <LoginForm />
    </div>
  );
};

// ---------------------------- Export ----------------------------
export default App;
