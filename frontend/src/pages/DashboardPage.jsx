import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Button from '../components/UI/Button';
import Alert from '../components/UI/Alert';
import { transcriptionService } from '../services/transcriptionService';
import { notesService } from '../services/notesService';

const DashboardPage = () => {
  const [transcripts, setTranscripts] = useState([]);
  const [notes, setNotes] = useState([]);
  const [transcriptionCount, setTranscriptionCount] = useState(0);
  const [noteCount, setNoteCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [summaryData, transcriptList, notesList] = await Promise.all([
        transcriptionService.getStatusSummary(),
        transcriptionService.getTranscripts(),
        notesService.getNotes(),
      ]);

      const totalTranscripts = summaryData?.total ?? transcriptList.length;
      setTranscriptionCount(totalTranscripts);
      setTranscripts(transcriptList.slice(0, 5));

      setNoteCount(notesList.length);
      setNotes(notesList.slice(0, 5));
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load workspace data. Please check your connection or try again.');
      setTranscriptionCount(null);
      setNoteCount(null);
      setTranscripts([]);
      setNotes([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const getStatusBadge = (status) => {
    const badges = {
      completed: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-400',
      processing: 'bg-blue-100 text-blue-800 dark:bg-blue-950/40 dark:text-blue-400',
      pending: 'bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-400',
      failed: 'bg-rose-100 text-rose-800 dark:bg-rose-950/40 dark:text-rose-400',
    };
    const badgeClass = badges[status] || 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300';

    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize ${badgeClass}`}>
        {status}
      </span>
    );
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <Navbar />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Workspace Action Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-[var(--border)] mb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-[var(--text-primary)]">
              Workspace
            </h1>
            <p className="text-sm text-[var(--text-secondary)] mt-1">
              Manage your recordings, transcripts, and notes.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link to="/transcriptions/new">
              <Button variant="primary" size="md">
                + New Transcription
              </Button>
            </Link>
          </div>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            <div className="flex justify-between items-center w-full">
              <span>{error}</span>
              <button
                onClick={loadDashboardData}
                className="text-xs font-semibold underline ml-4 hover:opacity-80"
              >
                Retry
              </button>
            </div>
          </Alert>
        )}

        {/* Small useful counts */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="bg-[var(--bg-surface)] p-4 rounded-lg border border-[var(--border)]">
            <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">
              Transcriptions
            </span>
            <p className="text-2xl font-bold text-[var(--text-primary)] mt-1">
              {loading ? '...' : error ? '—' : transcriptionCount}
            </p>
          </div>

          <div className="bg-[var(--bg-surface)] p-4 rounded-lg border border-[var(--border)]">
            <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">
              Notes
            </span>
            <p className="text-2xl font-bold text-[var(--text-primary)] mt-1">
              {loading ? '...' : error ? '—' : noteCount}
            </p>
          </div>
        </div>

        {/* Practical Work Area */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Transcriptions */}
          <div className="bg-[var(--bg-surface)] rounded-lg border border-[var(--border)] p-5">
            <div className="flex items-center justify-between pb-4 border-b border-[var(--border)] mb-4">
              <h2 className="text-base font-semibold text-[var(--text-primary)]">
                Recent Transcriptions
              </h2>
              <Link
                to="/transcriptions"
                className="text-xs font-medium text-[var(--primary)] hover:underline"
              >
                View all
              </Link>
            </div>

            {loading ? (
              <div className="py-8 text-center text-sm text-[var(--text-secondary)]">
                Loading transcriptions...
              </div>
            ) : error ? (
              <div className="py-8 text-center text-sm text-[var(--text-secondary)]">
                Failed to load transcriptions.
              </div>
            ) : transcripts.length === 0 ? (
              <div className="py-8 text-center">
                <p className="text-sm text-[var(--text-secondary)] mb-3">
                  No transcriptions yet.
                </p>
                <Link to="/transcriptions/new">
                  <Button variant="outline" size="sm">
                    Upload Recording
                  </Button>
                </Link>
              </div>
            ) : (
              <ul className="divide-y divide-[var(--border)]">
                {transcripts.map((t) => (
                  <li key={t.id} className="py-3 flex items-center justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                        {t.title || t.file_name}
                      </p>
                      <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                        {formatDate(t.created_at)}
                      </p>
                    </div>
                    <div>{getStatusBadge(t.status)}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Recent Notes */}
          <div className="bg-[var(--bg-surface)] rounded-lg border border-[var(--border)] p-5">
            <div className="flex items-center justify-between pb-4 border-b border-[var(--border)] mb-4">
              <h2 className="text-base font-semibold text-[var(--text-primary)]">
                Recent Notes
              </h2>
              <Link
                to="/notes"
                className="text-xs font-medium text-[var(--primary)] hover:underline"
              >
                View all
              </Link>
            </div>

            {loading ? (
              <div className="py-8 text-center text-sm text-[var(--text-secondary)]">
                Loading notes...
              </div>
            ) : error ? (
              <div className="py-8 text-center text-sm text-[var(--text-secondary)]">
                Failed to load notes.
              </div>
            ) : notes.length === 0 ? (
              <div className="py-8 text-center">
                <p className="text-sm text-[var(--text-secondary)] mb-3">
                  No notes created yet.
                </p>
                <Link to="/notes">
                  <Button variant="outline" size="sm">
                    Go to Notes
                  </Button>
                </Link>
              </div>
            ) : (
              <ul className="divide-y divide-[var(--border)]">
                {notes.map((n) => (
                  <li key={n.id} className="py-3">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                        {n.title}
                      </p>
                      <span className="text-xs text-[var(--text-secondary)] shrink-0">
                        {formatDate(n.created_at)}
                      </span>
                    </div>
                    {n.content && (
                      <p className="text-xs text-[var(--text-secondary)] mt-1 line-clamp-1">
                        {n.content}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
