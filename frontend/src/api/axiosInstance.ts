// ---------------------------- External Imports ----------------------------
// Import axios to create a custom instance
import axios from "axios";

// ---------------------------- Axios Instance ----------------------------
// Base URL comes from environment variable
// (Vite convention: must start with VITE_)
const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    withCredentials: true, // optional, if backend uses cookies/sessions
});

// ---------------------------- Export ----------------------------
export default api;
