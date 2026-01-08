import apiClient from './api';

export const trainingService = {
  createJob: (jobData) =>
    apiClient.post('/training/jobs', jobData),

  listJobs: () =>
    apiClient.get('/training/jobs'),

  getJob: (jobId) =>
    apiClient.get(`/training/jobs/${jobId}`),

  startTraining: (jobId) =>
    apiClient.post(`/training/jobs/${jobId}/start`),

  pauseTraining: (jobId) =>
    apiClient.post(`/training/jobs/${jobId}/pause`),

  cancelTraining: (jobId) =>
    apiClient.post(`/training/jobs/${jobId}/cancel`),

  deleteJob: (jobId) =>
    apiClient.delete(`/training/jobs/${jobId}`),

  listCheckpoints: (jobId) =>
    apiClient.get(`/training/checkpoints/${jobId}`),

  restoreCheckpoint: (checkpointId) =>
    apiClient.post(`/training/checkpoints/${checkpointId}/restore`)
};

export default trainingService;
