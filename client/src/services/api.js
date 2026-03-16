/**
 * Модуль для взаимодействия с FastAPI бэкендом.
 * Все запросы идут через axios с автоматическим добавлением JWT.
 */
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Перехватчик: добавляем JWT-токен к каждому запросу
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Перехватчик ответов: обработка 401 (refresh token)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', res.data.access_token);
          localStorage.setItem('refresh_token', res.data.refresh_token);
          // Повторяем исходный запрос
          error.config.headers.Authorization = `Bearer ${res.data.access_token}`;
          return api(error.config);
        } catch {
          // Refresh тоже истёк — выходим
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// ========== AUTH ==========
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
};

// ========== PRODUCTS ==========
export const productsAPI = {
  getAll: (params) => api.get('/products', { params }),
  getById: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
};

// ========== ORDERS ==========
export const ordersAPI = {
  create: (data) => api.post('/orders', data),
  getMy: (params) => api.get('/orders/my', { params }),
  getFarmerOrders: (params) => api.get('/orders/farmer', { params }),
  updateStatus: (id, data) => api.patch(`/orders/${id}/status`, data),
};

// ========== ANALYTICS ==========
export const analyticsAPI = {
  getSales: (period) => api.get('/analytics/sales', { params: { period } }),
};

export default api;