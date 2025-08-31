// ---------------------------- External Imports ----------------------------
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------
import settings from "../core/settings"; // centralized config file

// ---------------------------- Axios Instance ----------------------------
const api = axios.create({
    baseURL: settings.apiBaseUrl,  // now loaded from settings file
    withCredentials: true,         // optional if backend uses cookies/sessions
});

// ---------------------------- Export ----------------------------
export default api;
