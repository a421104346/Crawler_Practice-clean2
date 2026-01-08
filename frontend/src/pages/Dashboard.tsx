/**
 * 主仪表板页面
 * 显示爬虫控制面板和实时任务列表
 */
import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { CrawlerPanel } from '@/components/CrawlerPanel'
import { TaskCard } from '@/components/TaskCard'
import { taskApi } from '@/services/api'
import { useWebSocket } from '@/hooks/useWebSocket'
import type { Task } from '@/types'
import { LogOut, RefreshCw, History } from 'lucide-react'

export const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const { user, logout, isAuthenticated } = useAuthStore()
  
  const [tasks, setTasks] = useState<Task[]>([])
  const [activeTasks, setActiveTasks] = useState<Set<string>>(new Set())
  const [isRefreshing, setIsRefreshing] = useState(false)

  // 检查认证状态
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  // 加载任务列表
  const loadTasks = useCallback(async () => {
    try {
      const response = await taskApi.list({ page: 1, page_size: 20 })
      setTasks(response.tasks)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    }
  }, [])

  useEffect(() => {
    loadTasks()
  }, [loadTasks])

  // 刷新任务列表
  const handleRefresh = async () => {
    setIsRefreshing(true)
    await loadTasks()
    setTimeout(() => setIsRefreshing(false), 500)
  }

  // 处理新任务创建
  const handleTaskCreated = (taskId: string) => {
    // 添加到活跃任务集合
    setActiveTasks(prev => new Set(prev).add(taskId))
    
    // 立即刷新任务列表
    loadTasks()
  }

  // WebSocket 消息处理
  const handleWebSocketMessage = useCallback((message: any) => {
    setTasks(prevTasks => {
      const updatedTasks = prevTasks.map(task =>
        task.id === message.task_id
          ? { ...task, status: message.status, progress: message.progress }
          : task
      )
      
      // 如果任务不在列表中，重新加载
      const exists = prevTasks.some(t => t.id === message.task_id)
      if (!exists) {
        loadTasks()
      }
      
      return updatedTasks
    })
  }, [loadTasks])

  // 为每个活跃任务创建 WebSocket 连接
  activeTasks.forEach(taskId => {
    useWebSocket(taskId, { onMessage: handleWebSocketMessage })
  })

  // 处理删除任务
  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('确定要删除这个任务吗？')) return

    try {
      await taskApi.delete(taskId)
      setTasks(tasks.filter(t => t.id !== taskId))
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }

  // 处理下载结果
  const handleDownloadResult = (taskId: string) => {
    const task = tasks.find(t => t.id === taskId)
    if (!task?.result) return

    // 创建并下载 JSON 文件
    const dataStr = JSON.stringify(task.result, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `task_${taskId}_result.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  // 处理登出
  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">爬虫管理平台</h1>
            </div>
            
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                欢迎, <span className="font-medium">{user?.username}</span>
              </span>
              
              <button
                onClick={() => navigate('/history')}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
              >
                <History size={18} />
                历史记录
              </button>
              
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
              >
                <LogOut size={18} />
                登出
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 左侧：爬虫控制面板 */}
          <div className="lg:col-span-1">
            <CrawlerPanel onTaskCreated={handleTaskCreated} />
          </div>

          {/* 右侧：任务列表 */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                任务列表
                <span className="ml-3 text-sm font-normal text-gray-500">
                  ({tasks.length} 个任务)
                </span>
              </h2>
              
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
              >
                <RefreshCw
                  size={18}
                  className={isRefreshing ? 'animate-spin' : ''}
                />
                刷新
              </button>
            </div>

            {/* 任务卡片网格 */}
            {tasks.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">暂无任务</p>
                <p className="text-gray-400 text-sm mt-2">
                  使用左侧的控制面板创建新任务
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {tasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onDelete={handleDeleteTask}
                    onDownload={handleDownloadResult}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
