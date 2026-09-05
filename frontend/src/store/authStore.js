import { create } from 'zustand';

const useAuthStore = create((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,
  loading: true,
  theme: localStorage.getItem('theme') || 'light',

  setAuth: (user, accessToken) => set({
    user,
    accessToken,
    isAuthenticated: true
  }),

  setUser: (user) => set({ user }),

  logout: () => set({
    user: null,
    accessToken: null,
    isAuthenticated: false,
    loading: false
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
