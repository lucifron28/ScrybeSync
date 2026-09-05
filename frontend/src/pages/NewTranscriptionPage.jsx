import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Button from '../components/UI/Button';
import Input from '../components/UI/Input';
import Alert from '../components/UI/Alert';
import { transcriptionService } from '../services/transcriptionService';

const NewTranscriptionPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' | 'url'
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      if (!title) {
        setTitle(selected.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select an audio or video file.');
      return;
    }

    setIsUploading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', file);
    if (title.trim()) {
      formData.append('title', title.trim());
    }

    try {
      await transcriptionService.uploadTranscript(formData);
      setSuccess('File uploaded successfully! Transcription queued.');
      setTimeout(() => {
        navigate('/transcriptions');
      }, 1200);
    } catch (err) {
      const msg =
        err.response?.data?.file?.[0] ||
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to upload file. Ensure it is a supported audio/video format and within the size limit.';
      setError(msg);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <Navbar />

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-[var(--text-primary)]">
            New Transcription
          </h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            Choose an input source to transcribe your media.
          </p>
        </div>

        {/* Input Method Tabs */}
        <div className="flex border-b border-[var(--border)] mb-6 gap-6">
          <button
            type="button"
            onClick={() => setActiveTab('upload')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'upload'
                ? 'border-[var(--primary)] text-[var(--primary)]'
                : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            Upload File
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('url')}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'url'
                ? 'border-[var(--primary)] text-[var(--primary)]'
                : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            Import from URL
            <span className="text-xs bg-[var(--bg-surface-elevated)] px-1.5 py-0.5 rounded text-[var(--text-secondary)]">
              Planned
            </span>
          </button>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {success && (
          <Alert variant="success" className="mb-6">
            {success}
          </Alert>
        )}

        {activeTab === 'upload' ? (
          <form
            onSubmit={handleUploadSubmit}
            className="bg-[var(--bg-surface)] rounded-lg border border-[var(--border)] p-6 space-y-6"
          >
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                Audio or Video File
              </label>
              <input
                type="file"
                accept="audio/*,video/*,.mp3,.wav,.m4a,.flac,.ogg,.mp4,.avi,.mov,.mkv,.webm"
                onChange={handleFileChange}
                disabled={isUploading}
                className="w-full text-sm text-[var(--text-secondary)] file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-[var(--primary)] file:text-[var(--on-primary)] hover:file:opacity-90 file:cursor-pointer cursor-pointer border border-[var(--border)] rounded-lg p-2 bg-[var(--bg-surface)]"
              />
              <p className="text-xs text-[var(--text-secondary)] mt-2">
                Supported formats: MP3, WAV, M4A, FLAC, OGG, MP4, AVI, MOV, MKV, WEBM (Max 100MB).
              </p>
            </div>

            <Input
              label="Title (optional)"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Team Meeting, Lecture 1"
              disabled={isUploading}
            />

            <div className="flex justify-end gap-3 pt-4 border-t border-[var(--border)]">
              <Button
                variant="outline"
                type="button"
                onClick={() => navigate('/dashboard')}
                disabled={isUploading}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                type="submit"
                loading={isUploading}
                disabled={isUploading || !file}
              >
                {isUploading ? 'Uploading...' : 'Start Transcription'}
              </Button>
            </div>
          </form>
        ) : (
          <div className="bg-[var(--bg-surface)] rounded-lg border border-[var(--border)] p-6 space-y-6">
            <div className="p-4 bg-[var(--bg-surface-elevated)] rounded-lg border border-[var(--border)]">
              <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                Planned Feature
              </h3>
              <p className="text-sm text-[var(--text-secondary)]">
                Direct URL import via yt-dlp will be supported in an upcoming update. You will be able to paste YouTube or other supported media URLs and send audio directly to Whisper.
              </p>
            </div>

            <div>
              <Input
                label="Media URL"
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                disabled
              />
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-[var(--border)]">
              <Button
                variant="outline"
                type="button"
                onClick={() => setActiveTab('upload')}
              >
                Switch to File Upload
              </Button>
              <Button variant="primary" disabled>
                Import URL (Planned)
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default NewTranscriptionPage;
