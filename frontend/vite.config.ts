// ---------------------------- External Imports ----------------------------
// Import defineConfig to define Vite configuration
import { defineConfig } from "vite";

// Import the React plugin for Vite
import react from "@vitejs/plugin-react";

// Import Node's path module to resolve directory paths
import path from "path";

// ---------------------------- Vite Config ----------------------------
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Use "@" as an alias for the "src" directory
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
