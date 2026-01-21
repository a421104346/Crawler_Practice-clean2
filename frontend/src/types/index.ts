/**
 * 全局类型定义
 */

// 爬虫信息
export interface CrawlerInfo {
  name: string
  display_name: string
  description: string
  parameters: string[]
  optional_parameters: string[]
  status: 'active' | 'inactive'
}

// 任务状态
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

// 任务
export interface Task {
  id: string
  crawler_type: string
  status: TaskStatus
  progress: number
  params: Record<string, any> | null
  result: any | null
  error: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
  duration: number | null
  user_id: string | null
}

// 任务列表响应
export interface TaskListResponse {
  total: number
  tasks: Task[]
  page: number
  page_size: number
}

// WebSocket 消息类型
export type WebSocketMessageType = 'connection' | 'update' | 'complete' | 'error' | 'pong';

export interface BaseWebSocketMessage {
  type?: WebSocketMessageType;
  task_id?: string;
  message?: string;
}

// 连接欢迎消息
export interface ConnectionMessage extends BaseWebSocketMessage {
  type: 'connection';
  task_id: string;
  message: string;
}

// 心跳响应
export interface PongMessage extends BaseWebSocketMessage {
  type: 'pong';
}

// 任务更新消息（后端目前未发送 type 字段）
export interface TaskUpdateMessage extends BaseWebSocketMessage {
  task_id: string;
  status: TaskStatus;
  progress: number;
  message: string;
  result?: any;
  error?: string;
  type?: 'update' | 'complete' | 'error'; // 兼容性定义
}

export type WebSocketMessage = ConnectionMessage | PongMessage | TaskUpdateMessage;

// 用户
export interface User {
  id: string
  username: string
  email: string | null
  is_active: boolean
  is_admin: boolean
  created_at: string | null
  updated_at?: string
  last_login?: string
}

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应
export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// 注册请求
export interface RegisterRequest {
  username: string
  email?: string
  password: string
}

// API 响应
export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  data?: T
  error?: {
    code: string
    message: string
    details?: any
  }
  timestamp?: string
}

// 爬虫运行请求
export interface RunCrawlerRequest {
  symbol?: string
  page?: number
  max_pages?: number
  category?: string
  search?: string
  extra_params?: Record<string, any>
}

// Firecrawl
export type FirecrawlFormat = 'markdown' | 'html' | 'rawHtml' | 'screenshot' | 'json'

export interface FirecrawlScrapeRequest {
  url: string
  formats: FirecrawlFormat[]
  only_main_content: boolean
  wait_for?: number
  timeout_ms?: number
  cookie?: string
  headers?: Record<string, string>
}

export interface FirecrawlScrapeResponse {
  success: boolean
  data?: Record<string, unknown>
  error?: string
}

export interface FirecrawlWeiboHotRankRequest {
  pages?: number
  wait_for?: number
  timeout_ms?: number
  cookie?: string
}

export interface WeiboHotRankPost {
  username: string
  user_link: string
  content: string
}

export interface FirecrawlWeiboHotRankResult {
  topic_title: string
  topic_url: string
  pages: number
  total_posts: number
  posts: WeiboHotRankPost[]
}

export interface FirecrawlWeiboHotRankResponse {
  success: boolean
  data?: FirecrawlWeiboHotRankResult
  error?: string
}

// 健康检查响应
export interface HealthResponse {
  status: 'healthy' | 'unhealthy' | 'degraded'
  timestamp: string
  checks?: {
    database: { status: string; message: string }
    redis: { status: string; message: string }
    celery: { status: string; message: string }
  }
}

// 统计数据
export interface StatsResponse {
  tasks: {
    total: number
    completed: number
    failed: number
    running: number
    success_rate: number
  }
  uptime: string
}
