import {
  FirecrawlScrapeRequest,
  FirecrawlScrapeResponse,
  FirecrawlWeiboHotRankRequest,
  FirecrawlWeiboHotRankResponse
} from '../types';
import axios from 'axios';
import {
  demoAdminApi,
  demoAuthApi,
  demoCrawlerApi,
  demoFirecrawlApi,
  demoMonitoringApi,
  demoTaskApi
} from './demoApi';

const trimTrailingSlash = (value: string): string => value.replace(/\/+$/, '');

const resolveApiBaseUrl = (): string => {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  if (configuredBaseUrl) {
    return trimTrailingSlash(configuredBaseUrl);
  }

  // Fallback keeps local/dev and reverse-proxy deployments working out of the box.
  if (typeof window !== 'undefined') {
    return `${window.location.origin}/api`;
  }

  return 'http://localhost:8000/api';
};

const API_URL = resolveApiBaseUrl();
export const isDemoModeEnabled = import.meta.env.VITE_DEMO_MODE === 'true';

// Create axios instance with interceptor for auth
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const isTokenExpired = (token: string): boolean => {
  try {
    const [, payload] = token.split('.');
    if (!payload) return true;
    const decoded = JSON.parse(atob(payload));
    const exp = typeof decoded?.exp === 'number' ? decoded.exp * 1000 : 0;
    return !exp || Date.now() >= exp;
  } catch {
    return true;
  }
};

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token && !isTokenExpired(token)) {
    config.headers.Authorization = `Bearer ${token}`;
  } else if (token) {
    localStorage.removeItem('access_token');
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const url: string = error?.config?.url || '';
    const isAuthRoute = url.includes('/auth/login') || url.includes('/auth/register');
    if (status === 401) {
      localStorage.removeItem('access_token');
      if (!isAuthRoute && typeof window !== 'undefined') {
        const path = window.location.pathname || '';
        if (path !== '/login') {
          window.location.assign('/login?reason=expired');
        }
      }
    }
    if (status === 403 && typeof window !== 'undefined') {
      const path = window.location.pathname || '';
      const isAdminRoute = path.startsWith('/admin');
      if (isAdminRoute) {
        window.location.assign('/dashboard');
        return Promise.reject(error);
      }
      if (!isAuthRoute && path !== '/login') {
        localStorage.removeItem('access_token');
        window.location.assign('/login?reason=expired');
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (username: string, password: string) => {
    if (isDemoModeEnabled) {
      return demoAuthApi.login(username, password);
    }
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
  
  register: async (username: string, email: string | null, password: string) => {
    if (isDemoModeEnabled) {
      return demoAuthApi.register(username, email, password);
    }
    const response = await api.post('/auth/register', { username, email, password });
    return response.data;
  },
  
  getCurrentUser: async () => {
    if (isDemoModeEnabled) {
      return demoAuthApi.getCurrentUser();
    }
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  logout: async () => {
    if (isDemoModeEnabled) {
      return demoAuthApi.logout();
    }
    const response = await api.post('/auth/logout');
    return response.data;
  },
};

export const taskApi = {
  createTask: async (crawlerType: string, params: any) => {
    if (isDemoModeEnabled) {
      return demoTaskApi.createTask(crawlerType, params);
    }
    const response = await api.post(`/crawlers/${crawlerType}/run`, params);
    return response.data;
  },
  
  getTasks: async (page = 1, pageSize = 20) => {
    if (isDemoModeEnabled) {
      return demoTaskApi.getTasks(page, pageSize);
    }
    const response = await api.get(`/tasks?page=${page}&page_size=${pageSize}`);
    return response.data;
  },
  
  list: async (params: { page: number, page_size: number }) => {
    if (isDemoModeEnabled) {
      return demoTaskApi.list(params);
    }
    const response = await api.get(`/tasks?page=${params.page}&page_size=${params.page_size}`);
    return response.data;
  },

  get: async (taskId: string) => {
    if (isDemoModeEnabled) {
      return demoTaskApi.get(taskId);
    }
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  },
  
  getTask: async (taskId: string) => {
    if (isDemoModeEnabled) {
      return demoTaskApi.getTask(taskId);
    }
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  },
  
  cancelTask: async (taskId: string) => {
    if (isDemoModeEnabled) {
      return demoTaskApi.cancelTask(taskId);
    }
    const response = await api.post(`/tasks/${taskId}/cancel`);
    return response.data;
  },
  
  delete: async (taskId: string) => {
    if (isDemoModeEnabled) {
      return demoTaskApi.delete(taskId);
    }
    const response = await api.delete(`/tasks/${taskId}`);
    return response.data;
  },

  deleteTask: async (taskId: string) => {
    if (isDemoModeEnabled) {
      return demoTaskApi.deleteTask(taskId);
    }
    const response = await api.delete(`/tasks/${taskId}`);
    return response.data;
  },
};

export const crawlerApi = {
  list: async () => {
    if (isDemoModeEnabled) {
      return demoCrawlerApi.list();
    }
    const response = await api.get('/crawlers');
    return response.data;
  },

  getCrawlers: async () => {
    if (isDemoModeEnabled) {
      return demoCrawlerApi.getCrawlers();
    }
    const response = await api.get('/crawlers');
    return response.data;
  },
  
  getCrawlerInfo: async (crawlerType: string) => {
    if (isDemoModeEnabled) {
      return demoCrawlerApi.getCrawlerInfo(crawlerType);
    }
    const response = await api.get(`/crawlers/${crawlerType}`);
    return response.data;
  },

  run: async (crawlerType: string, params: any) => {
    if (isDemoModeEnabled) {
      return demoCrawlerApi.run(crawlerType, params);
    }
    const response = await api.post(`/crawlers/${crawlerType}/run`, params);
    return response.data;
  }
};

export const adminApi = {
  getUsers: async (skip = 0, limit = 100) => {
    if (isDemoModeEnabled) {
      return demoAdminApi.getUsers();
    }
    const response = await api.get(`/admin/users?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  
  deleteUser: async (userId: string) => {
    if (isDemoModeEnabled) {
      return demoAdminApi.deleteUser(userId);
    }
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  },
  
  getAllTasks: async (page = 1, pageSize = 20) => {
    if (isDemoModeEnabled) {
      return demoAdminApi.getAllTasks(page, pageSize);
    }
    const response = await api.get(`/admin/tasks?page=${page}&page_size=${pageSize}`);
    return response.data;
  },
  
  deleteTask: async (taskId: string) => {
    if (isDemoModeEnabled) {
      return demoAdminApi.deleteTask(taskId);
    }
    const response = await api.delete(`/admin/tasks/${taskId}`);
    return response.data;
  },
};

export const monitoringApi = {
  stats: async () => {
    if (isDemoModeEnabled) {
      return demoMonitoringApi.stats();
    }
    const response = await api.get('/monitoring/stats');
    return response.data;
  },

  health: async () => {
    if (isDemoModeEnabled) {
      return demoMonitoringApi.health();
    }
    const response = await api.get('/monitoring/health');
    return response.data;
  },

  detailedHealth: async () => {
    if (isDemoModeEnabled) {
      return demoMonitoringApi.detailedHealth();
    }
    const response = await api.get('/monitoring/health/detailed');
    return response.data;
  },

  metrics: async () => {
    if (isDemoModeEnabled) {
      return demoMonitoringApi.metrics();
    }
    const response = await api.get('/monitoring/metrics');
    return response.data;
  }
};

export const firecrawlApi = {
  scrape: async (payload: FirecrawlScrapeRequest): Promise<FirecrawlScrapeResponse> => {
    if (isDemoModeEnabled) {
      return demoFirecrawlApi.scrape(payload);
    }
    const response = await api.post('/firecrawl/scrape', payload);
    return response.data;
  },
  weiboHotRank1: async (
    payload: FirecrawlWeiboHotRankRequest
  ): Promise<FirecrawlWeiboHotRankResponse> => {
    if (isDemoModeEnabled) {
      return demoFirecrawlApi.weiboHotRank1(payload);
    }
    const response = await api.post('/firecrawl/weibo/hot-rank1', payload);
    return response.data;
  }
};

export default api;
