/**
 * API 服务层
 * 封装所有后端 API 调用
 */
import axios, { AxiosError, AxiosInstance } from 'axios'
import type {
  CrawlerInfo,
  Task,
  TaskListResponse,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  User,
  RunCrawlerRequest,
  HealthResponse,
  StatsResponse,
} from '@/types'

// 创建 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // 如果是 401 错误
    if (error.response?.status === 401) {
      // 如果是登录接口本身的 401，不进行跳转，直接抛出错误供 UI 处理
      if (error.config?.url?.includes('/auth/login')) {
        return Promise.reject(error)
      }

      // 其他接口的 401 代表 Token 过期，清除并跳转登录
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ========== 认证 API ==========

export const authApi = {
  // 登录
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  // 注册
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post<User>('/auth/register', data)
    return response.data
  },

  // 获取当前用户信息
  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  // 登出
  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
    localStorage.removeItem('access_token')
  },
}

// ========== 爬虫 API ==========

export const crawlerApi = {
  // 获取所有爬虫列表
  list: async (): Promise<CrawlerInfo[]> => {
    const response = await api.get<CrawlerInfo[]>('/crawlers')
    return response.data
  },

  // 获取特定爬虫信息
  getInfo: async (crawlerType: string): Promise<CrawlerInfo> => {
    const response = await api.get<CrawlerInfo>(`/crawlers/${crawlerType}`)
    return response.data
  },

  // 运行爬虫
  run: async (
    crawlerType: string,
    params: RunCrawlerRequest
  ): Promise<{ task_id: string; status: string; message: string }> => {
    const response = await api.post(`/crawlers/${crawlerType}/run`, params)
    return response.data
  },
}

// ========== 任务 API ==========

export const taskApi = {
  // 获取任务列表
  list: async (params?: {
    page?: number
    page_size?: number
    status?: string
    crawler_type?: string
  }): Promise<TaskListResponse> => {
    const response = await api.get<TaskListResponse>('/tasks', { params })
    return response.data
  },

  // 获取任务详情
  get: async (taskId: string): Promise<Task> => {
    const response = await api.get<Task>(`/tasks/${taskId}`)
    return response.data
  },

  // 更新任务
  update: async (
    taskId: string,
    data: { status?: string; progress?: number }
  ): Promise<Task> => {
    const response = await api.patch<Task>(`/tasks/${taskId}`, data)
    return response.data
  },

  // 删除任务
  delete: async (taskId: string): Promise<void> => {
    await api.delete(`/tasks/${taskId}`)
  },
}

// ========== 监控 API ==========

export const monitoringApi = {
  // 健康检查
  health: async (): Promise<HealthResponse> => {
    const response = await api.get<HealthResponse>('/monitoring/health/detailed')
    return response.data
  },

  // 统计数据
  stats: async (): Promise<StatsResponse> => {
    const response = await api.get<StatsResponse>('/monitoring/stats')
    return response.data
  },
}

export default api
