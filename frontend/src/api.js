import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Products API
export const productsAPI = {
  search: (query) => api.get('/products', { params: { q: query } }),
  getAll: () => api.get('/products/all'),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
};

// Sales API
export const salesAPI = {
  getAll: (status) => api.get('/sales', { params: { status } }),
  create: (data) => api.post('/sales', data),
  updateStatus: (id, data) => api.put(`/sales/${id}/status`, data),
  delete: (id) => api.delete(`/sales/${id}`),
};

// Stock History API
export const historyAPI = {
  getHistory: (params) => api.get('/stock-history', { params }),
};

export default api;
