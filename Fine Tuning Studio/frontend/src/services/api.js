import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add authorization token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (username, email, password, fullName) =>
    apiClient.post('/auth/register', { username, email, password, full_name: fullName }),

  login: (username, password) =>
    apiClient.post('/auth/login', { username, password }),

  createApiKey: (name) =>
    apiClient.post('/auth/create-api-key', { name }),

  listApiKeys: () =>
    apiClient.get('/auth/api-keys'),

  deleteApiKey: (keyId) =>
    apiClient.delete(`/auth/api-keys/${keyId}`),
};

export const modelsAPI = {
  getSupportedModels: () =>
    apiClient.get('/models/supported'),

  listModels: () =>
    apiClient.get('/models'),

  getModel: (modelId) =>
    apiClient.get(`/models/${modelId}`),

  createModel: (modelData) =>
    apiClient.post('/models', modelData),

  updateModel: (modelId, modelData) =>
    apiClient.put(`/models/${modelId}`, modelData),

  deleteModel: (modelId) =>
    apiClient.delete(`/models/${modelId}`),
};

export const healthAPI = {
  check: () =>
    apiClient.get('/health'),

  ping: () =>
    apiClient.get('/ping'),
};

export default apiClient;
