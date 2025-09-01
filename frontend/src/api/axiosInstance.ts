// ---------------------------- External Imports ----------------------------
import axios from "axios";

// ---------------------------- Internal Imports ----------------------------
import settings from "../core/settings"; // centralized config file

// ---------------------------- Axios Instance ----------------------------
const api = axios.create({
    baseURL: settings.apiBaseUrl,  // now loaded from settings file
    withCredentials: true,         // Backend uses cookies
});

// ---------------------------- Export ----------------------------
export default api;
