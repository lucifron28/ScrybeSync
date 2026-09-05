import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Button from '../components/UI/Button';
import Alert from '../components/UI/Alert';
import { transcriptionService } from '../services/transcriptionService';

const TranscriptionsPage = () => {
  const [transcripts, setTranscripts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryingId, setRetryingId] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  const fetchTranscripts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await transcriptionService.getTranscripts();
      setTranscripts(data);
    } catch (err) {
      console.error('Failed to fetch transcripts:', err);
      setError('Failed to load transcriptions.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTranscripts();
  }, [fetchTranscripts]);

  const handleRetry = async (id) => {
    setRetryingId(id);
    try {
      await transcriptionService.retryTranscript(id);
      await fetchTranscripts();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to retry transcription.');
    } finally {
      setRetryingId(null);
    }
  };

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
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <Navbar />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-[var(--border)] mb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-[var(--text-primary)]">
              Transcriptions
            </h1>
            <p className="text-sm text-[var(--text-secondary)] mt-1">
              Your audio and video speech-to-text recordings.
            </p>
          </div>

          <Link to="/transcriptions/new">
            <Button variant="primary" size="md">
              + New Transcription
            </Button>
          </Link>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            <div className="flex justify-between items-center w-full">
              <span>{error}</span>
              <button
                onClick={fetchTranscripts}
                className="text-xs font-semibold underline ml-4 hover:opacity-80"
              >
                Retry
              </button>
            </div>
          </Alert>
        )}

        {loading ? (
          <div className="py-16 text-center text-sm text-[var(--text-secondary)]">
            Loading transcriptions...
          </div>
        ) : transcripts.length === 0 ? (
          <div className="bg-[var(--bg-surface)] rounded-lg border border-[var(--border)] p-12 text-center">
            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-1">
              No transcriptions yet
            </h2>
            <p className="text-sm text-[var(--text-secondary)] mb-6">
              Upload an audio or video recording to generate your first transcript.
            </p>
            <Link to="/transcriptions/new">
              <Button variant="primary" size="md">
                Upload Recording
              </Button>
            </Link>
          </div>
        ) : (
          <div className="bg-[var(--bg-surface)] rounded-lg border border-[var(--border)] overflow-hidden">
            <ul className="divide-y divide-[var(--border)]">
              {transcripts.map((t) => (
                <li key={t.id} className="p-4 sm:p-5">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-[var(--text-primary)]">
                          {t.title || t.file_name}
                        </span>
                        {getStatusBadge(t.status)}
                      </div>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[var(--text-secondary)] mt-1">
                        <span>File: {t.file_name}</span>
                        {t.duration && (
                          <span>Duration: {Math.round(t.duration)}s</span>
                        )}
                        <span>{formatDate(t.created_at)}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 mt-2 sm:mt-0">
                      {t.status === 'failed' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleRetry(t.id)}
                          loading={retryingId === t.id}
                        >
                          Retry
                        </Button>
                      )}

                      {t.raw_text && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            setExpandedId(expandedId === t.id ? null : t.id)
                          }
                        >
                          {expandedId === t.id ? 'Hide Transcript' : 'View Transcript'}
                        </Button>
                      )}
                    </div>
                  </div>

                  {t.error_message && (
                    <div className="mt-3 p-3 bg-rose-50 dark:bg-rose-950/20 text-rose-800 dark:text-rose-400 text-xs rounded border border-rose-200 dark:border-rose-900/30">
                      Error: {t.error_message}
                    </div>
                  )}

                  {expandedId === t.id && t.raw_text && (
                    <div className="mt-4 p-4 bg-[var(--bg-surface-elevated)] rounded border border-[var(--border)]">
                      <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-2">
                        Transcript Text
                      </h3>
                      <p className="text-sm text-[var(--text-primary)] whitespace-pre-wrap leading-relaxed font-mono">
                        {t.raw_text}
                      </p>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </main>
    </div>
  );
};

export default TranscriptionsPage;
