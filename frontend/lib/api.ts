import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Automatically attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints
export const registerUser = (data: { email: string; full_name: string; password: string }) =>
  api.post('/auth/register', data);

export const loginUser = (data: { email: string; password: string }) =>
  api.post('/auth/login', data);

export const getMe = () => api.get('/auth/me');

// Scan endpoints
export const uploadDocument = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/scan/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getScanHistory = () => api.get('/scan/history');

export const getScanResult = (scanId: string) => api.get(`/scan/${scanId}/result`);

export const downloadReport = (scanId: string) =>
  api.get(`/scan/${scanId}/report`, { responseType: 'blob' });

// Admin endpoints
export const addTemplate = (data: {
  institution_name: string;
  document_type: string;
  document_description: string;
  sha256_hash: string;
}) => api.post('/admin/templates', data);

export const getTemplates = () => api.get('/admin/templates');

export default api;