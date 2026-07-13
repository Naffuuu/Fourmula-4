import axios from "axios";

// Access token lives in memory only (not localStorage) to reduce XSS blast
// radius. The refresh token lives in an httpOnly cookie the browser sends
// automatically, so the JS layer never touches it directly.
let accessToken = null;
let onUnauthorized = () => {};

export function setAccessToken(token) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
}

export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

export const api = axios.create({
  baseURL: "/api/v1",
  withCredentials: true, // sends the httpOnly refresh-token cookie
});

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

let refreshInFlight = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url.includes("/auth/refresh")) {
      originalRequest._retry = true;
      try {
        refreshInFlight =
          refreshInFlight ||
          axios.post("/api/v1/auth/refresh", {}, { withCredentials: true }).finally(() => {
            refreshInFlight = null;
          });
        const { data } = await refreshInFlight;
        setAccessToken(data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        setAccessToken(null);
        onUnauthorized();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
