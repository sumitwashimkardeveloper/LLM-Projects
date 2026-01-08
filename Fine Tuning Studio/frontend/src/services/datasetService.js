import apiClient from './api';

export const datasetService = {
  uploadDataset: (file, name, description) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    formData.append('description', description);

    return apiClient.post('/datasets', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  listDatasets: () =>
    apiClient.get('/datasets'),

  getDataset: (datasetId) =>
    apiClient.get(`/datasets/${datasetId}`),

  previewDataset: (datasetId, limit = 10) =>
    apiClient.get(`/datasets/${datasetId}/preview`, { params: { limit } }),

  splitDataset: (datasetId, trainRatio = 0.8, valRatio = 0.1, testRatio = 0.1) =>
    apiClient.post(`/datasets/${datasetId}/split`, {
      train_ratio: trainRatio,
      val_ratio: valRatio,
      test_ratio: testRatio
    }),

  deleteDataset: (datasetId) =>
    apiClient.delete(`/datasets/${datasetId}`)
};

export default datasetService;
