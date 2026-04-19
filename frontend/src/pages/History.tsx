/**
 * Task history page
 * Displays all historical tasks and statistics
 */
import React, { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Filter, TrendingUp, TrendingDown, Activity } from 'lucide-react'
import { taskApi, monitoringApi } from '@/services/api'
import { TaskCard } from '@/components/TaskCard'
import type { Task, TaskStatus, StatsResponse } from '@/types'
import { Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate()
  
  const [tasks, setTasks] = useState<Task[]>([])
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [filterStatus, setFilterStatus] = useState<TaskStatus | 'all'>('all')
  const [filterCrawler, setFilterCrawler] = useState<string>('all')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  // Load data
  useEffect(() => {
    loadTasks()
    loadStats()
  }, [page, filterStatus, filterCrawler])

  const loadTasks = async () => {
    setIsLoading(true)
    try {
      const params: any = { page, page_size: 20 }
      
      if (filterStatus !== 'all') {
        params.status = filterStatus
      }
      
      if (filterCrawler !== 'all') {
        params.crawler_type = filterCrawler
      }
      
      const response = await taskApi.list(params)
      setTasks(response.tasks)
      setTotal(response.total)
      setSelectedIds(new Set())
    } catch (error) {
      console.error('Failed to load tasks:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const data = await monitoringApi.stats()
      setStats(data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  const selectedCount = useMemo(() => selectedIds.size, [selectedIds])

  // Handle delete
  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return
    if (!confirm('This action cannot be undone. Confirm delete?')) return

    try {
      await taskApi.delete(taskId)
      setTasks(tasks.filter(t => t.id !== taskId))
      setSelectedIds((prev) => {
        const next = new Set(prev)
        next.delete(taskId)
        return next
      })
      loadStats() // Reload stats
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }

  const toggleSelect = (taskId: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(taskId)) {
        next.delete(taskId)
      } else {
        next.add(taskId)
      }
      return next
    })
  }

  const toggleSelectAll = () => {
    setSelectedIds((prev) => {
      if (prev.size === tasks.length) {
        return new Set()
      }
      return new Set(tasks.map((task) => task.id))
    })
  }

  const handleBatchDelete = async () => {
    if (selectedIds.size === 0) return
    if (!confirm(`Are you sure you want to delete ${selectedIds.size} selected tasks?`)) return
    if (!confirm('This action cannot be undone. Confirm delete?')) return

    const ids = Array.from(selectedIds)
    const results = await Promise.allSettled(ids.map((id) => taskApi.delete(id)))
    const successIds = new Set(
      results
        .map((result, index) => ({ result, id: ids[index] }))
        .filter((entry) => entry.result.status === 'fulfilled')
        .map((entry) => entry.id)
    )

    if (successIds.size > 0) {
      setTasks((prev) => prev.filter((task) => !successIds.has(task.id)))
      setSelectedIds((prev) => {
        const next = new Set(prev)
        successIds.forEach((id) => next.delete(id))
        return next
      })
      loadStats()
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

  // Pie chart data
  const pieData = stats ? [
    { name: 'Completed', value: stats.tasks.completed, color: '#10b981' },
    { name: 'Failed', value: stats.tasks.failed, color: '#ef4444' },
    { name: 'Running', value: stats.tasks.running, color: '#3b82f6' },
  ].filter(d => d.value > 0) : []

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 text-gray-700 hover:text-gray-900"
            >
              <ArrowLeft size={20} />
              Back to Dashboard
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Tasks</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {stats.tasks.total}
                  </p>
                </div>
                <Activity className="text-gray-400" size={32} />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Completed</p>
                  <p className="text-2xl font-bold text-green-600 mt-1">
                    {stats.tasks.completed}
                  </p>
                </div>
                <TrendingUp className="text-green-400" size={32} />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Failed</p>
                  <p className="text-2xl font-bold text-red-600 mt-1">
                    {stats.tasks.failed}
                  </p>
                </div>
                <TrendingDown className="text-red-400" size={32} />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">
                    {(stats.tasks.success_rate * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="text-blue-400 text-2xl font-bold">
                  ✓
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Chart area */}
        {stats && pieData.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Status Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center gap-4">
            <Filter size={20} className="text-gray-400" />
            
            <div className="flex-1 grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="all">All</option>
                  <option value="pending">Pending</option>
                  <option value="running">Running</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Crawler Type
                </label>
                <select
                  value={filterCrawler}
                  onChange={(e) => setFilterCrawler(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="all">All</option>
                  <option value="yahoo">Yahoo Finance</option>
                  <option value="movies">Douban Movies</option>
                  <option value="jobs">Job Listings</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Task list */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              Task History ({total})
            </h2>
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 text-sm text-gray-600">
                <input
                  type="checkbox"
                  checked={tasks.length > 0 && selectedIds.size === tasks.length}
                  onChange={toggleSelectAll}
                  disabled={tasks.length === 0}
                  className="h-4 w-4"
                />
                Select All
              </label>
              <button
                onClick={handleBatchDelete}
                disabled={selectedCount === 0}
                className="px-3 py-2 text-sm bg-red-50 text-red-600 rounded-lg disabled:opacity-50 hover:bg-red-100 transition"
              >
                Batch Delete ({selectedCount})
              </button>
            </div>
          </div>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-gray-500 mt-4">Loading...</p>
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-500">No matching tasks found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {tasks.map((task) => (
                <div key={task.id} className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(task.id)}
                    onChange={() => toggleSelect(task.id)}
                    className="mt-3 h-4 w-4"
                  />
                  <div className="flex-1">
                    <TaskCard
                      task={task}
                      onDelete={handleDeleteTask}
                      onDownload={handleDownloadResult}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {total > 20 && (
            <div className="flex justify-center gap-2 mt-6">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-4 py-2">
                Page {page} of {Math.ceil(total / 20)}
              </span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={page >= Math.ceil(total / 20)}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
