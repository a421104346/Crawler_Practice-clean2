import { Task, User } from '../types';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Create axios instance with interceptor for auth
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
  
  register: async (username, email, password) => {
    const response = await api.post('/auth/register', { username, email, password });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
};

export const taskApi = {
  createTask: async (crawlerType: string, params: any) => {
    const response = await api.post(`/crawlers/${crawlerType}/run`, params);
    return response.data;
  },
  
  getTasks: async (page = 1, pageSize = 20) => {
    const response = await api.get(`/tasks?page=${page}&page_size=${pageSize}`);
    return response.data;
  },
  
  list: async (params: { page: number, page_size: number }) => {
    const response = await api.get(`/tasks?page=${params.page}&page_size=${params.page_size}`);
    return response.data;
  },

  get: async (taskId: string) => {
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  },
  
  getTask: async (taskId: string) => {
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  },
  
  cancelTask: async (taskId: string) => {
    const response = await api.post(`/tasks/${taskId}/cancel`);
    return response.data;
  },
  
  delete: async (taskId: string) => {
    const response = await api.delete(`/tasks/${taskId}`);
    return response.data;
  },

  deleteTask: async (taskId: string) => {
    const response = await api.delete(`/tasks/${taskId}`);
    return response.data;
  },
};

export const crawlerApi = {
  list: async () => {
    const response = await api.get('/crawlers');
    return response.data;
  },

  getCrawlers: async () => {
    const response = await api.get('/crawlers');
    return response.data;
  },
  
  getCrawlerInfo: async (crawlerType: string) => {
    const response = await api.get(`/crawlers/${crawlerType}`);
    return response.data;
  },

  run: async (crawlerType: string, params: any) => {
    const response = await api.post(`/crawlers/${crawlerType}/run`, params);
    return response.data;
  }
};

export const adminApi = {
  getUsers: async (skip = 0, limit = 100) => {
    const response = await api.get(`/admin/users?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  
  deleteUser: async (userId: string) => {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  },
  
  getAllTasks: async (page = 1, pageSize = 20) => {
    const response = await api.get(`/admin/tasks?page=${page}&page_size=${pageSize}`);
    return response.data;
  },
  
  deleteTask: async (taskId: string) => {
    const response = await api.delete(`/admin/tasks/${taskId}`);
    return response.data;
  },
};

export const monitoringApi = {
  stats: async () => {
    const response = await api.get('/monitoring/stats');
    return response.data;
  },

  health: async () => {
    const response = await api.get('/monitoring/health');
    return response.data;
  },

  detailedHealth: async () => {
    const response = await api.get('/monitoring/health/detailed');
    return response.data;
  },

  metrics: async () => {
    const response = await api.get('/monitoring/metrics');
    return response.data;
  }
};

export default api;
