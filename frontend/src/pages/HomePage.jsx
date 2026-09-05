import { Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import Button from '../components/UI/Button';

const HomePage = () => {
  const { theme, toggleTheme } = useAuthStore();

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <header className="bg-[var(--bg-surface)] border-b border-[var(--border)]">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <span className="text-xl font-bold tracking-tight text-[var(--text-primary)]">
                ScrybeSync
              </span>
            </div>

            <div className="flex items-center space-x-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleTheme}
                className="p-2"
                aria-label="Toggle theme"
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
                  Sign In
                </Button>
              </Link>

              <Link to="/register">
                <Button variant="primary" size="sm">
                  Create Account
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h1 className="text-3xl sm:text-4xl font-bold text-[var(--text-primary)] mb-4 tracking-tight">
            ScrybeSync
          </h1>
          <p className="text-lg text-[var(--text-secondary)] mb-8">
            Transcribe recordings, summarize them, and turn them into notes.
          </p>

          <div className="flex flex-row gap-3 justify-center">
            <Link to="/login">
              <Button variant="outline" size="md">
                Sign In
              </Button>
            </Link>
            <Link to="/register">
              <Button variant="primary" size="md">
                Create Account
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8 border-t border-[var(--border)]">
          <div className="bg-[var(--bg-surface)] p-6 rounded-lg border border-[var(--border)]">
            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-2">
              Transcription
            </h2>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Upload audio or video files to generate speech-to-text transcripts powered by Whisper.
            </p>
          </div>

          <div className="bg-[var(--bg-surface)] p-6 rounded-lg border border-[var(--border)]">
            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-2">
              Summarization
            </h2>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Generate structured summaries, key points, and actionable takeaways from completed transcripts.
            </p>
          </div>

          <div className="bg-[var(--bg-surface)] p-6 rounded-lg border border-[var(--border)]">
            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-2">
              Notes
            </h2>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Organize your insights into markdown notes categorized for easy reference and personal retrieval.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default HomePage;
