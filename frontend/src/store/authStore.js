import { create } from 'zustand';

const useAuthStore = create((set, get) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,
  loading: false,
  theme: localStorage.getItem('theme') || 'light',

  setAuth: (user, accessToken) => set({
    user,
    accessToken,
    isAuthenticated: true
  }),

  logout: () => set({
    user: null,
    accessToken: null,
    isAuthenticated: false
  }),

  setLoading: (loading) => set({ loading }),

  setAccessToken: (accessToken) => set({ accessToken }),

  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', newTheme);
    return { theme: newTheme };
  }),

  setTheme: (theme) => {
    localStorage.setItem('theme', theme);
    set({ theme });
  },
}));

export default useAuthStore;
