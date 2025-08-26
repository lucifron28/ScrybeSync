import api from './api';

export const authService = {
  login: async (credentials) => {
    const response = await api.post('/users/login/', credentials);
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/users/register/', userData);
    return response.data;
  },

  logout: async () => {
    await api.post('/users/logout/');
  },

  refreshToken: async () => {
    const response = await api.post('/users/token/refresh/');
    return response.data;
  },
};
