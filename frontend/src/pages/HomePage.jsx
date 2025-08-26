import { Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import Button from '../components/UI/Button';

const HomePage = () => {
  const { theme, toggleTheme } = useAuthStore();

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
              
              <Link to="/login">
                <Button variant="outline" size="sm">
                  Sign in
                </Button>
              </Link>
              
              <Link to="/register">
                <Button variant="primary" size="sm">
                  Get started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-[var(--text-primary)] mb-6">
              Transform Audio to
              <span className="text-[var(--primary)]"> Organized Notes</span>
            </h1>
            <p className="text-xl text-[var(--text-secondary)] mb-8 max-w-3xl mx-auto">
              ScrybeSync transcribes your audio recordings and automatically organizes them into 
              searchable, categorized notes. Perfect for meetings, lectures, interviews, and more.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register">
                <Button variant="primary" size="lg" className="w-full sm:w-auto">
                  Start Free Trial
                </Button>
              </Link>
              <Link to="/demo">
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  Watch Demo
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="bg-[var(--bg-surface)] border-t border-[var(--border)]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
            <h2 className="text-3xl font-bold text-center text-[var(--text-primary)] mb-12">
              Everything you need to organize your audio content
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-[var(--primary)] text-[var(--on-primary)] rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 016 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">
                  AI Transcription
                </h3>
                <p className="text-[var(--text-secondary)]">
                  Accurate speech-to-text powered by advanced AI technology
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-[var(--secondary)] text-[var(--on-secondary)] rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">
                  Smart Organization
                </h3>
                <p className="text-[var(--text-secondary)]">
                  Automatically categorize and tag your notes for easy retrieval
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-[var(--success)] text-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">
                  Powerful Search
                </h3>
                <p className="text-[var(--text-secondary)]">
                  Find any content instantly with full-text search capabilities
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default HomePage;
