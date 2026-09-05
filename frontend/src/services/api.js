import axios from 'axios';
import useAuthStore from '../store/authStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dedicated unintercepted client for token refresh to avoid interceptor recursion
const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

let refreshPromise = null;

api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If there is no response or it's not a 401, reject immediately
    if (!error.response || error.response.status !== 401) {
      return Promise.reject(error);
    }

    // Do not attempt refresh on auth endpoints (login, register, token refresh) or already retried requests
    const requestUrl = originalRequest?.url || '';
    const isAuthEndpoint =
      requestUrl.includes('/users/login/') ||
      requestUrl.includes('/users/register/') ||
      requestUrl.includes('/users/token/refresh/');

    if (isAuthEndpoint || originalRequest?._retry) {
      if (requestUrl.includes('/users/token/refresh/')) {
        useAuthStore.getState().logout();
      }
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (!refreshPromise) {
      refreshPromise = refreshClient
        .post('/users/token/refresh/')
        .then(async (response) => {
          const newToken = response.data.access_token;
          useAuthStore.getState().setAccessToken(newToken);

          // Restore user profile if missing in store
          if (!useAuthStore.getState().user) {
            try {
              const meRes = await refreshClient.get('/users/me/', {
                headers: { Authorization: `Bearer ${newToken}` },
              });
              useAuthStore.getState().setUser(meRes.data);
            } catch {
              // Non-fatal if user profile restore fails
            }
          }
          return newToken;
        })
        .catch((refreshError) => {
          useAuthStore.getState().logout();
          return Promise.reject(refreshError);
        })
        .finally(() => {
          refreshPromise = null;
        });
    }

    try {
      const newToken = await refreshPromise;
      originalRequest.headers.Authorization = `Bearer ${newToken}`;
      return api(originalRequest);
    } catch (refreshErr) {
      return Promise.reject(refreshErr);
    }
  }
);

export default api;
