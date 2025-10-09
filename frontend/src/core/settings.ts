// ---------------------------- Frontend Settings ----------------------------
// Centralized frontend setting for API base URL
const settings = {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL, // loaded from Vite env
};

// ---------------------------- Export ----------------------------
// Export settings object for use throughout the frontend
export default settings;
