import api from './api';

export const notesService = {
  getNotes: async () => {
    const response = await api.get('/notes/notes/');
    return response.data;
  },

  getNote: async (id) => {
    const response = await api.get(`/notes/notes/${id}/`);
    return response.data;
  },

  createNote: async (noteData) => {
    const response = await api.post('/notes/notes/', noteData);
    return response.data;
  },

  updateNote: async (id, noteData) => {
    const response = await api.patch(`/notes/notes/${id}/`, noteData);
    return response.data;
  },

  deleteNote: async (id) => {
    const response = await api.delete(`/notes/notes/${id}/`);
    return response.data;
  },

  getCategories: async () => {
    const response = await api.get('/notes/categories/');
    return response.data;
  },

  createCategory: async (categoryData) => {
    const response = await api.post('/notes/categories/', categoryData);
    return response.data;
  },
};
