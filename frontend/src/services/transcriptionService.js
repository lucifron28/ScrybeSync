import api from './api';

export const transcriptionService = {
  getTranscripts: async () => {
    const response = await api.get('/transcriber/transcripts/');
    return response.data;
  },

  getStatusSummary: async () => {
    const response = await api.get('/transcriber/transcripts/status_summary/');
    return response.data;
  },

  getTranscript: async (id) => {
    const response = await api.get(`/transcriber/transcripts/${id}/`);
    return response.data;
  },

  uploadTranscript: async (formData) => {
    const response = await api.post('/transcriber/transcripts/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  retryTranscript: async (id) => {
    const response = await api.post(`/transcriber/transcripts/${id}/retry_transcription/`);
    return response.data;
  },

  deleteTranscript: async (id) => {
    const response = await api.delete(`/transcriber/transcripts/${id}/`);
    return response.data;
  },
};
