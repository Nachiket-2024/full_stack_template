// Centralized settings for the frontend (mirrors backend settings.py style)
export const settings = {
    // Backend API base URL (must be defined in .env via VITE_API_BASE_URL)
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL as string,
};
