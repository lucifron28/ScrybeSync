import { useState, useEffect, useCallback } from 'react';
import Navbar from '../components/Navbar';
import Button from '../components/UI/Button';
import Input from '../components/UI/Input';
import Alert from '../components/UI/Alert';
import { notesService } from '../services/notesService';

const NotesPage = () => {
  const [notes, setNotes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCreatingNote, setIsCreatingNote] = useState(false);
  const [isCreatingCategory, setIsCreatingCategory] = useState(false);

  // Form states
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Category form state
  const [newCategoryName, setNewCategoryName] = useState('');
  const [categorySubmitting, setCategorySubmitting] = useState(false);

  const fetchNotesAndCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [notesData, categoriesData] = await Promise.all([
        notesService.getNotes(),
        notesService.getCategories(),
      ]);
      setNotes(notesData);
      setCategories(categoriesData);
    } catch (err) {
      console.error('Failed to load notes or categories:', err);
      setError('Failed to load notes data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotesAndCategories();
  }, [fetchNotesAndCategories]);

  const handleCreateNote = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const payload = {
        title: newTitle.trim(),
        content: newContent,
      };
      if (selectedCategory) {
        payload.category = parseInt(selectedCategory, 10);
      }

      await notesService.createNote(payload);
      setNewTitle('');
      setNewContent('');
      setSelectedCategory('');
      setIsCreatingNote(false);
      await fetchNotesAndCategories();
    } catch (err) {
      setError(
        err.response?.data?.category?.[0] ||
        err.response?.data?.title?.[0] ||
        'Failed to create note.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateCategory = async (e) => {
    e.preventDefault();
    if (!newCategoryName.trim()) return;

    setCategorySubmitting(true);
    setError(null);

    try {
      await notesService.createCategory({ name: newCategoryName.trim() });
      setNewCategoryName('');
      setIsCreatingCategory(false);
      await fetchNotesAndCategories();
    } catch (err) {
      setError(
        err.response?.data?.name?.[0] ||
        err.response?.data?.name ||
        'Failed to create category.'
      );
    } finally {
      setCategorySubmitting(false);
    }
  };

  const handleDeleteNote = async (id) => {
    if (!window.confirm('Are you sure you want to delete this note?')) return;

    try {
      await notesService.deleteNote(id);
      await fetchNotesAndCategories();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to delete note.');
    }
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

  const getCategoryName = (categoryId) => {
    const cat = categories.find((c) => c.id === categoryId);
    return cat ? cat.name : null;
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <Navbar />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-[var(--border)] mb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-[var(--text-primary)]">
              Notes
            </h1>
            <p className="text-sm text-[var(--text-secondary)] mt-1">
              Organize and reference your notes and insights.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="md"
              onClick={() => setIsCreatingCategory(!isCreatingCategory)}
            >
              + Category
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={() => setIsCreatingNote(!isCreatingNote)}
            >
              + New Note
            </Button>
          </div>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {/* Inline Category Creation */}
        {isCreatingCategory && (
          <div className="bg-[var(--bg-surface)] p-5 rounded-lg border border-[var(--border)] mb-6">
            <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-3">
              Add New Category
            </h2>
            <form onSubmit={handleCreateCategory} className="flex gap-3">
              <Input
                type="text"
                placeholder="Category name (e.g. Work, School, Research)"
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                className="flex-1"
                disabled={categorySubmitting}
                required
              />
              <Button
                variant="primary"
                type="submit"
                loading={categorySubmitting}
                disabled={categorySubmitting || !newCategoryName.trim()}
              >
                Save
              </Button>
              <Button
                variant="ghost"
                type="button"
                onClick={() => setIsCreatingCategory(false)}
              >
                Cancel
              </Button>
            </form>
          </div>
        )}

        {/* Inline Note Creation */}
        {isCreatingNote && (
          <div className="bg-[var(--bg-surface)] p-6 rounded-lg border border-[var(--border)] mb-6">
            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
              Create Note
            </h2>
            <form onSubmit={handleCreateNote} className="space-y-4">
              <Input
                label="Title"
                type="text"
                placeholder="Note title"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                required
              />

              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                  Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--bg-surface)] text-[var(--text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                >
                  <option value="">No category</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                  Content
                </label>
                <textarea
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  placeholder="Write your note in Markdown..."
                  rows={5}
                  className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--bg-surface)] text-[var(--text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] font-mono"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-[var(--border)]">
                <Button
                  variant="outline"
                  type="button"
                  onClick={() => setIsCreatingNote(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  type="submit"
                  loading={isSubmitting}
                  disabled={isSubmitting || !newTitle.trim()}
                >
                  Create Note
                </Button>
              </div>
            </form>
          </div>
        )}

        {/* Notes Listing */}
        {loading ? (
          <div className="py-16 text-center text-sm text-[var(--text-secondary)]">
            Loading notes...
          </div>
        ) : notes.length === 0 ? (
          <div className="bg-[var(--bg-surface)] rounded-lg border border-[var(--border)] p-12 text-center">
            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-1">
              No notes yet
            </h2>
            <p className="text-sm text-[var(--text-secondary)] mb-6">
              Create your first note to organize your insights and summaries.
            </p>
            <Button
              variant="primary"
              size="md"
              onClick={() => setIsCreatingNote(true)}
            >
              + Create Note
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {notes.map((n) => {
              const categoryName = getCategoryName(n.category);

              return (
                <div
                  key={n.id}
                  className="bg-[var(--bg-surface)] rounded-lg border border-[var(--border)] p-5 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h3 className="text-base font-semibold text-[var(--text-primary)] break-words">
                        {n.title}
                      </h3>
                      <button
                        onClick={() => handleDeleteNote(n.id)}
                        className="text-xs text-[var(--text-secondary)] hover:text-[var(--error)] p-1 transition-colors"
                        title="Delete note"
                      >
                        Delete
                      </button>
                    </div>

                    {categoryName && (
                      <span className="inline-block text-xs font-medium px-2 py-0.5 rounded bg-[var(--bg-surface-elevated)] text-[var(--text-secondary)] mb-3">
                        {categoryName}
                      </span>
                    )}

                    {n.content && (
                      <p className="text-sm text-[var(--text-secondary)] whitespace-pre-wrap line-clamp-4 leading-relaxed font-mono text-xs">
                        {n.content}
                      </p>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-[var(--border)] text-xs text-[var(--text-secondary)]">
                    {formatDate(n.created_at)}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
};

export default NotesPage;
