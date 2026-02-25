import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useTaskStore } from '@/store/taskStore'
import { CrawlerPanel } from '@/components/CrawlerPanel'
import { TaskCard } from '@/components/TaskCard'
import { taskApi } from '@/services/api'
import { LogOut, RefreshCw, History, Shield, FlaskConical, Flame } from 'lucide-react'

export const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const { user, logout, isAuthenticated } = useAuthStore()
  const { tasks, setTasks, addTask } = useTaskStore()
  
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Check auth status
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  // Load task list
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

  // Refresh task list
  const handleRefresh = async () => {
    setIsRefreshing(true)
    await loadTasks()
    setTimeout(() => setIsRefreshing(false), 500)
  }

  // Handle new task creation
  const handleTaskCreated = async (taskId: string) => {
    // Fetch new task details and add to store
    try {
        const newTask = await taskApi.get(taskId)
        addTask(newTask)
    } catch (error) {
        console.error('Failed to fetch new task:', error)
        loadTasks() // Fallback: refresh full list
    }
  }

  // Handle result download
  const handleDownloadResult = (taskId: string) => {
    const task = tasks.find(t => t.id === taskId)
    if (!task?.result) return

    // Create and download JSON file
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

  // Handle logout
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
      {/* Top navigation bar */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Crawler Management Platform</h1>
            </div>
            
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                Welcome, <span className="font-medium">{user?.username}</span>
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
                History
              </button>

              <button
                onClick={() => navigate('/firecrawl')}
                className="flex items-center gap-2 px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
              >
                <FlaskConical size={18} />
                Firecrawl Test
              </button>

              <button
                onClick={() => navigate('/firecrawl/hot-rank1')}
                className="flex items-center gap-2 px-4 py-2 text-orange-600 hover:bg-orange-50 rounded-lg transition"
              >
                <Flame size={18} />
                Hot Rank1
              </button>
              
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
              >
                <LogOut size={18} />
                Log Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content area */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Crawler control panel */}
          <div className="lg:col-span-1">
            <CrawlerPanel onTaskCreated={handleTaskCreated} />
          </div>

          {/* Right: Task list */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                Task List
                <span className="ml-3 text-sm font-normal text-gray-500">
                  ({visibleTasks.length} tasks)
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
                Refresh
              </button>
            </div>

            {/* Task card grid */}
            {visibleTasks.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No tasks yet</p>
                <p className="text-gray-400 text-sm mt-2">
                  Use the control panel on the left to create a new task
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
