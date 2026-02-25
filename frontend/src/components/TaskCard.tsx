/**
 * Task card component
 * Displays individual task info and status
 */
import React, { useCallback } from 'react'
import { formatDistanceToNow } from 'date-fns'
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
  // Import store for state updates
  const { updateTask } = useTaskStore()

  // Fetch latest task status
  const fetchLatestTask = useCallback(async () => {
    try {
      const latestTask = await taskApi.get(task.id)
      updateTask(task.id, latestTask)
    } catch (error) {
      console.error('Failed to fetch latest task:', error)
    }
  }, [task.id, updateTask])

  // WebSocket connection management
  // Only connect when task is running or pending
  const shouldConnect = task.status === 'running' || task.status === 'pending'
  
  useWebSocket(shouldConnect ? task.id : null, {
    onOpen: () => {
      // console.log('WebSocket connected, fetching latest status...')
      // Fetch latest status on connect in case we missed updates
      fetchLatestTask()
    },
    onMessage: (msg) => {
      // console.log('TaskCard received message:', msg)
      
      // Ignore connection welcome and heartbeat messages
      if (msg.type === 'connection' || msg.type === 'pong') {
        return
      }

      // Type guard: check if this is a task update message
      // Backend updates may lack type field but always include status
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

  // Status icon and color
  const getStatusConfig = (status: Task['status']) => {
    switch (status) {
      case 'pending':
        return { icon: Clock, color: 'text-gray-500', bg: 'bg-gray-100', label: 'Pending' }
      case 'running':
        return { icon: Loader2, color: 'text-blue-500', bg: 'bg-blue-100', label: 'Running', spin: true }
      case 'completed':
        return { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-100', label: 'Completed' }
      case 'failed':
        return { icon: XCircle, color: 'text-red-500', bg: 'bg-red-100', label: 'Failed' }
      case 'cancelled':
        return { icon: XCircle, color: 'text-gray-500', bg: 'bg-gray-100', label: 'Cancelled' }
      default:
        // Default/unknown status
        return { icon: Clock, color: 'text-gray-400', bg: 'bg-gray-50', label: status || 'Unknown' }
    }
  }

  const statusConfig = getStatusConfig(task.status)
  const StatusIcon = statusConfig.icon

  // Format time
  const createdAt = task.created_at.endsWith('Z') ? task.created_at : `${task.created_at}Z`
  
  const timeAgo = formatDistanceToNow(new Date(createdAt), {
    addSuffix: true,
  })

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {task.crawler_type}
          </h3>
          <p className="text-sm text-gray-500">
            {task.id.substring(0, 8)}... · {timeAgo}
          </p>
        </div>
        
        {/* Status badge */}
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

      {/* Progress bar */}
      {task.status === 'running' && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Progress</span>
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

      {/* Parameters */}
      {task.params && Object.keys(task.params).length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Parameters</p>
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

      {/* Error info */}
      {task.error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700 font-medium mb-1">Error</p>
          <p className="text-sm text-red-600">{task.error}</p>
        </div>
      )}

      {/* Duration */}
      {task.duration && (
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            Duration: <span className="font-medium">{task.duration.toFixed(2)}s</span>
          </p>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-2 pt-4 border-t border-gray-200">
        {task.status === 'completed' && onDownload && (
          <button
            onClick={() => onDownload(task.id)}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            <Download size={16} />
            Download Result
          </button>
        )}
        
        {onDelete && (
          <button
            onClick={() => onDelete(task.id)}
            className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition"
            title="Delete task"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>
    </div>
  )
}
