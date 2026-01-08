/**
 * 任务历史页面
 * 显示所有历史任务和统计信息
 */
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Filter, TrendingUp, TrendingDown, Activity } from 'lucide-react'
import { taskApi, monitoringApi } from '@/services/api'
import { TaskCard } from '@/components/TaskCard'
import type { Task, TaskStatus, StatsResponse } from '@/types'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate()
  
  const [tasks, setTasks] = useState<Task[]>([])
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [filterStatus, setFilterStatus] = useState<TaskStatus | 'all'>('all')
  const [filterCrawler, setFilterCrawler] = useState<string>('all')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)

  // 加载数据
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

  // 处理删除
  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('确定要删除这个任务吗？')) return

    try {
      await taskApi.delete(taskId)
      setTasks(tasks.filter(t => t.id !== taskId))
      loadStats() // 重新加载统计
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }

  // 饼图数据
  const pieData = stats ? [
    { name: '已完成', value: stats.tasks.completed, color: '#10b981' },
    { name: '失败', value: stats.tasks.failed, color: '#ef4444' },
    { name: '运行中', value: stats.tasks.running, color: '#3b82f6' },
  ].filter(d => d.value > 0) : []

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 text-gray-700 hover:text-gray-900"
            >
              <ArrowLeft size={20} />
              返回控制台
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 统计卡片 */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">总任务数</p>
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
                  <p className="text-sm text-gray-600">已完成</p>
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
                  <p className="text-sm text-gray-600">失败</p>
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
                  <p className="text-sm text-gray-600">成功率</p>
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

        {/* 图表区域 */}
        {stats && pieData.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">任务状态分布</h3>
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

        {/* 过滤器 */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center gap-4">
            <Filter size={20} className="text-gray-400" />
            
            <div className="flex-1 grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  状态
                </label>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="all">全部</option>
                  <option value="pending">等待中</option>
                  <option value="running">运行中</option>
                  <option value="completed">已完成</option>
                  <option value="failed">失败</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  爬虫类型
                </label>
                <select
                  value={filterCrawler}
                  onChange={(e) => setFilterCrawler(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="all">全部</option>
                  <option value="yahoo">Yahoo Finance</option>
                  <option value="movies">豆瓣电影</option>
                  <option value="jobs">招聘信息</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* 任务列表 */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              任务历史 ({total} 个)
            </h2>
          </div>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-gray-500 mt-4">加载中...</p>
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-500">暂无符合条件的任务</p>
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

          {/* 分页 */}
          {total > 20 && (
            <div className="flex justify-center gap-2 mt-6">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
              >
                上一页
              </button>
              <span className="px-4 py-2">
                第 {page} 页 / 共 {Math.ceil(total / 20)} 页
              </span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={page >= Math.ceil(total / 20)}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
              >
                下一页
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
