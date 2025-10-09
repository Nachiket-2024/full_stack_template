// ---------------------------- External Imports ----------------------------
// Import Axios HTTP client for making API requests
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------
// Import centralized settings containing API base URL
import settings from "../core/settings";

// ---------------------------- Axios Instance ----------------------------
// Create a reusable Axios instance with base configuration
const api = axios.create({
    // Set the base URL dynamically from settings
    baseURL: settings.apiBaseUrl,
    // Include credentials such as cookies in cross-site requests
    withCredentials: true,
});

// ---------------------------- Export ----------------------------
// Export the configured Axios instance for use across the app
export default api;
