import { useState } from 'react';
import useAuthStore from '../store/authStore';
import { authService } from '../services/authService';
import Button from '../components/UI/Button';

const DashboardPage = () => {
  const { user, logout, theme, toggleTheme } = useAuthStore();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      logout();
      setIsLoggingOut(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <header className="bg-[var(--bg-surface)] border-b border-[var(--border)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                ScrybeSync
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleTheme}
                className="p-2"
              >
                {theme === 'light' ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                )}
              </Button>
              
              <span className="text-[var(--text-secondary)]">
                Welcome, {user?.first_name || user?.username}!
              </span>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                loading={isLoggingOut}
              >
                Sign out
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-[var(--bg-surface)] rounded-lg border border-[var(--border)] p-6">
            <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
              Dashboard
            </h2>
            <p className="text-[var(--text-secondary)]">
              Welcome to ScrybeSync! This is your dashboard where you can manage your transcribed notes.
            </p>
            
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-[var(--bg-surface-elevated)] p-4 rounded-lg border border-[var(--border)]">
                <h3 className="text-lg font-medium text-[var(--text-primary)]">Notes</h3>
                <p className="text-2xl font-bold text-[var(--primary)] mt-2">0</p>
                <p className="text-sm text-[var(--text-secondary)]">Total notes created</p>
              </div>
              
              <div className="bg-[var(--bg-surface-elevated)] p-4 rounded-lg border border-[var(--border)]">
                <h3 className="text-lg font-medium text-[var(--text-primary)]">Categories</h3>
                <p className="text-2xl font-bold text-[var(--secondary)] mt-2">0</p>
                <p className="text-sm text-[var(--text-secondary)]">Categories created</p>
              </div>
              
              <div className="bg-[var(--bg-surface-elevated)] p-4 rounded-lg border border-[var(--border)]">
                <h3 className="text-lg font-medium text-[var(--text-primary)]">Transcriptions</h3>
                <p className="text-2xl font-bold text-[var(--success)] mt-2">0</p>
                <p className="text-sm text-[var(--text-secondary)]">Files transcribed</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
