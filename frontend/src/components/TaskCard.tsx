/**
 * 任务卡片组件
 * 显示单个任务的信息和状态
 */
import React, { useCallback } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { Clock, CheckCircle, XCircle, Loader2, Download, Trash2 } from 'lucide-react'
import type { Task } from '@/types'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useTaskStore } from '@/store/taskStore'
import { taskApi } from '@/services/api'
import clsx from 'clsx'

interface TaskCardProps {
  task: Task
  onDelete?: (taskId: string) => void
  onDownload?: (taskId: string) => void
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, onDelete, onDownload }) => {
  // 引入 store 用于更新状态
  const { updateTask } = useTaskStore()

  // 拉取最新任务状态
  const fetchLatestTask = useCallback(async () => {
    try {
      const latestTask = await taskApi.get(task.id)
      updateTask(task.id, latestTask)
    } catch (error) {
      console.error('Failed to fetch latest task:', error)
    }
  }, [task.id, updateTask])

  // WebSocket 连接管理
  // 只有当任务处于运行中或等待中才连接
  const shouldConnect = task.status === 'running' || task.status === 'pending'
  
  useWebSocket(shouldConnect ? task.id : null, {
    onOpen: () => {
      // console.log('WebSocket connected, fetching latest status...')
      // 连接建立后，立即拉取一次最新状态，以防错过由于断连导致的完成消息
      fetchLatestTask()
    },
    onMessage: (msg) => {
      // console.log('TaskCard received message:', msg)
      
      // 忽略连接建立时的欢迎消息和心跳消息
      if (msg.type === 'connection' || msg.type === 'pong') {
        return
      }

      // 使用类型保护检查是否为任务更新消息
      // 后端发送的任务更新消息可能没有 type 字段，但一定包含 status
      if ('status' in msg) {
        updateTask(msg.task_id, {
          status: msg.status,
          progress: msg.progress,
          result: msg.result,
          error: msg.error
        })
      }
    }
  })

  // 状态图标和颜色
  const getStatusConfig = (status: Task['status']) => {
    switch (status) {
      case 'pending':
        return { icon: Clock, color: 'text-gray-500', bg: 'bg-gray-100', label: '等待中' }
      case 'running':
        return { icon: Loader2, color: 'text-blue-500', bg: 'bg-blue-100', label: '运行中', spin: true }
      case 'completed':
        return { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-100', label: '已完成' }
      case 'failed':
        return { icon: XCircle, color: 'text-red-500', bg: 'bg-red-100', label: '失败' }
      case 'cancelled':
        return { icon: XCircle, color: 'text-gray-500', bg: 'bg-gray-100', label: '已取消' }
      default:
        // 默认/未知状态处理
        return { icon: Clock, color: 'text-gray-400', bg: 'bg-gray-50', label: status || '未知' }
    }
  }

  const statusConfig = getStatusConfig(task.status)
  const StatusIcon = statusConfig.icon

  // 格式化时间
  // 假设后端返回的是 UTC 时间但没有时区信息，手动添加 Z 后缀使其被解析为 UTC
  // 这样 formatDistanceToNow 就能正确计算相对于本地当前时间的差值
  const createdAt = task.created_at.endsWith('Z') ? task.created_at : `${task.created_at}Z`
  
  const timeAgo = formatDistanceToNow(new Date(createdAt), {
    addSuffix: true,
    locale: zhCN,
  })

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* 头部 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {task.crawler_type}
          </h3>
          <p className="text-sm text-gray-500">
            {task.id.substring(0, 8)}... · {timeAgo}
          </p>
        </div>
        
        {/* 状态徽章 */}
        <div className={clsx(
          'flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium',
          statusConfig.bg,
          statusConfig.color
        )}>
          <StatusIcon
            size={16}
            className={statusConfig.spin ? 'animate-spin' : ''}
          />
          {statusConfig.label}
        </div>
      </div>

      {/* 进度条 */}
      {task.status === 'running' && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">进度</span>
            <span className="text-sm font-medium text-blue-600">{task.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${task.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* 参数 */}
      {task.params && Object.keys(task.params).length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">参数</p>
          <div className="bg-gray-50 rounded-lg p-3 space-y-1">
            {Object.entries(task.params).map(([key, value]) => (
              <div key={key} className="flex items-center gap-2 text-sm">
                <span className="text-gray-600">{key}:</span>
                <span className="font-mono text-gray-900">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 错误信息 */}
      {task.error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700 font-medium mb-1">错误</p>
          <p className="text-sm text-red-600">{task.error}</p>
        </div>
      )}

      {/* 执行时间 */}
      {task.duration && (
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            执行时间: <span className="font-medium">{task.duration.toFixed(2)}s</span>
          </p>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex gap-2 pt-4 border-t border-gray-200">
        {task.status === 'completed' && onDownload && (
          <button
            onClick={() => onDownload(task.id)}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            <Download size={16} />
            下载结果
          </button>
        )}
        
        {onDelete && (
          <button
            onClick={() => onDelete(task.id)}
            className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition"
            title="删除任务"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>
    </div>
  )
}
