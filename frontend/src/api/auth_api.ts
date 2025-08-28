// ---------------------------- External Imports ----------------------------
// Import configured Axios instance
import api from "./axiosInstance";

// ---------------------------- Auth API Calls ----------------------------

// POST /auth/signup
export const signupApi = (payload: { name: string; email: string; password: string }) =>
    api.post("/auth/signup", payload);

// POST /auth/login
export const loginApi = (payload: { email: string; password: string }) =>
    api.post("/auth/login", payload);

// GET /auth/oauth2/login/google
export const oauth2LoginGoogleApi = () =>
    api.get("/auth/oauth2/login/google");

// GET /auth/oauth2/callback/google
export const oauth2CallbackGoogleApi = (code: string) =>
    api.get("/auth/oauth2/callback/google", { params: { code } });

// POST /auth/logout
export const logoutApi = (payload: { refresh_token: string }) =>
    api.post("/auth/logout", payload);

// POST /auth/logout/all
export const logoutAllApi = (payload: { refresh_token: string }) =>
    api.post("/auth/logout/all", payload);

// POST /auth/password-reset/request
export const passwordResetRequestApi = (payload: { email: string }) =>
    api.post("/auth/password-reset/request", payload);

// POST /auth/password-reset/confirm
export const passwordResetConfirmApi = (payload: { token: string; new_password: string }) =>
    api.post("/auth/password-reset/confirm", payload);

// GET /auth/verify-account?token=...&email=...
export const verifyAccountApi = (token: string, email: string) =>
    api.get("/auth/verify-account", { params: { token, email } });
