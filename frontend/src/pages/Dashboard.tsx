import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useTaskStore } from '@/store/taskStore'
import { CrawlerPanel } from '@/components/CrawlerPanel'
import { TaskCard } from '@/components/TaskCard'
import { taskApi } from '@/services/api'
import { LogOut, RefreshCw, History, Shield, FlaskConical } from 'lucide-react'

export const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const { user, logout, isAuthenticated } = useAuthStore()
  const { tasks, setTasks, addTask } = useTaskStore()
  
  const [isRefreshing, setIsRefreshing] = useState(false)

  // 检查认证状态
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  // 加载任务列表
  const loadTasks = useCallback(async () => {
    if (!isAuthenticated) {
      return
    }
    try {
      const response = await taskApi.list({ page: 1, page_size: 20 })
      setTasks(response.tasks)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    }
  }, [isAuthenticated, setTasks])

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
  const handleTaskCreated = async (taskId: string) => {
    // 获取新任务详情并添加到 store
    try {
        const newTask = await taskApi.get(taskId)
        addTask(newTask)
    } catch (error) {
        console.error('Failed to fetch new task:', error)
        loadTasks() // 降级方案：刷新整个列表
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

  const visibleTasks = useMemo(() => {
    const activeTasks = tasks.filter(
      (task) => task.status === 'running' || task.status === 'pending'
    )

    const completedTasks = tasks
      .filter((task) => task.status === 'completed')
      .sort((a, b) => {
        const aTime = Date.parse(a.created_at.endsWith('Z') ? a.created_at : `${a.created_at}Z`)
        const bTime = Date.parse(b.created_at.endsWith('Z') ? b.created_at : `${b.created_at}Z`)
        return bTime - aTime
      })
      .slice(0, 5)

    return [...activeTasks, ...completedTasks]
  }, [tasks])

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
              
              {user?.is_admin && (
                <button
                  onClick={() => navigate('/admin')}
                  className="flex items-center gap-2 px-4 py-2 text-purple-600 hover:bg-purple-50 rounded-lg transition"
                >
                  <Shield size={18} />
                  Admin
                </button>
              )}

              <button
                onClick={() => navigate('/history')}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
              >
                <History size={18} />
                历史记录
              </button>

              <button
                onClick={() => navigate('/firecrawl')}
                className="flex items-center gap-2 px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
              >
                <FlaskConical size={18} />
                Firecrawl 测试
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
                  ({visibleTasks.length} 个任务)
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
            {visibleTasks.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">暂无任务</p>
                <p className="text-gray-400 text-sm mt-2">
                  使用左侧的控制面板创建新任务
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {visibleTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
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
