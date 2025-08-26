import { useEffect } from 'react';
import useAuthStore from '../store/authStore';

const ThemeProvider = ({ children }) => {
  const { theme } = useAuthStore();

  useEffect(() => {
    const root = document.documentElement;
    
    if (theme === 'dark') {
      root.style.setProperty('--bg-primary', '#0B1220');
      root.style.setProperty('--bg-surface', '#0F172A');
      root.style.setProperty('--bg-surface-elevated', '#111827');
      root.style.setProperty('--text-primary', '#E5E7EB');
      root.style.setProperty('--text-secondary', '#94A3B8');
      root.style.setProperty('--border', '#334155');
      root.style.setProperty('--primary', '#60A5FA');
      root.style.setProperty('--on-primary', '#0B1220');
      root.style.setProperty('--secondary', '#FBBF24');
      root.style.setProperty('--on-secondary', '#0B1220');
      root.style.setProperty('--success', '#34D399');
      root.style.setProperty('--warning', '#F59E0B');
      root.style.setProperty('--error', '#F87171');
    } else {
      root.style.setProperty('--bg-primary', '#F8FAFC');
      root.style.setProperty('--bg-surface', '#FFFFFF');
      root.style.setProperty('--bg-surface-elevated', '#F1F5F9');
      root.style.setProperty('--text-primary', '#0F172A');
      root.style.setProperty('--text-secondary', '#475569');
      root.style.setProperty('--border', '#E2E8F0');
      root.style.setProperty('--primary', '#3B82F6');
      root.style.setProperty('--on-primary', '#FFFFFF');
      root.style.setProperty('--secondary', '#F59E0B');
      root.style.setProperty('--on-secondary', '#0F172A');
      root.style.setProperty('--success', '#10B981');
      root.style.setProperty('--warning', '#F59E0B');
      root.style.setProperty('--error', '#EF4444');
    }
  }, [theme]);

  return <div className={`min-h-screen transition-colors duration-200 ${theme}`}>{children}</div>;
};

export default ThemeProvider;
