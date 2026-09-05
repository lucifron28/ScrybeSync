import { useState } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { authService } from '../services/authService';
import Button from './UI/Button';

const Navbar = () => {
  const navigate = useNavigate();
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
      navigate('/login');
    }
  };

  const navLinkClass = ({ isActive }) =>
    `text-sm font-medium px-3 py-1.5 rounded-md transition-colors ${
      isActive
        ? 'bg-[var(--bg-surface-elevated)] text-[var(--primary)]'
        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface-elevated)]'
    }`;

  return (
    <header className="bg-[var(--bg-surface)] border-b border-[var(--border)] sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-6">
            <Link to="/dashboard" className="flex items-center">
              <span className="text-lg font-bold tracking-tight text-[var(--text-primary)]">
                ScrybeSync
              </span>
            </Link>

            <nav className="hidden sm:flex items-center space-x-1">
              <NavLink to="/dashboard" className={navLinkClass} end>
                Dashboard
              </NavLink>
              <NavLink to="/transcriptions" className={navLinkClass}>
                Transcriptions
              </NavLink>
              <NavLink to="/notes" className={navLinkClass}>
                Notes
              </NavLink>
            </nav>
          </div>

          <div className="flex items-center space-x-3">
            <Link to="/transcriptions/new">
              <Button variant="primary" size="sm" className="hidden sm:inline-flex">
                + New Transcription
              </Button>
            </Link>

            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className="p-2"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              )}
            </Button>

            {user && (
              <span className="text-xs sm:text-sm text-[var(--text-secondary)] font-medium max-w-[120px] sm:max-w-[200px] truncate">
                {user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.username}
              </span>
            )}

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

        {/* Mobile secondary navigation */}
        <div className="flex sm:hidden items-center justify-between pb-3 pt-1 border-t border-[var(--border)] gap-2">
          <div className="flex space-x-1">
            <NavLink to="/dashboard" className={navLinkClass} end>
              Dashboard
            </NavLink>
            <NavLink to="/transcriptions" className={navLinkClass}>
              Transcriptions
            </NavLink>
            <NavLink to="/notes" className={navLinkClass}>
              Notes
            </NavLink>
          </div>
          <Link to="/transcriptions/new">
            <Button variant="primary" size="sm">
              + New
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
