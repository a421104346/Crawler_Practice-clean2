/**
 * 爬虫控制面板组件
 * 用于选择爬虫类型和设置参数
 */
import React, { useState, useEffect } from 'react'
import { Play, Loader2 } from 'lucide-react'
import { crawlerApi } from '@/services/api'
import type { CrawlerInfo, RunCrawlerRequest } from '@/types'

interface CrawlerPanelProps {
  onTaskCreated: (taskId: string) => void
}

export const CrawlerPanel: React.FC<CrawlerPanelProps> = ({ onTaskCreated }) => {
  const [crawlers, setCrawlers] = useState<CrawlerInfo[]>([])
  const [selectedCrawler, setSelectedCrawler] = useState<string>('')
  const [params, setParams] = useState<Record<string, string>>({})
  const [isRunning, setIsRunning] = useState(false)
  const [error, setError] = useState<string>('')

  // 加载爬虫列表
  useEffect(() => {
    loadCrawlers()
  }, [])

  const loadCrawlers = async () => {
    try {
      const data = await crawlerApi.list()
      setCrawlers(data)
      if (data.length > 0) {
        setSelectedCrawler(data[0].name)
      }
    } catch (error) {
      console.error('Failed to load crawlers:', error)
    }
  }

  // 获取当前选中爬虫的信息
  const currentCrawler = crawlers.find(c => c.name === selectedCrawler)

  // 处理参数变化
  const handleParamChange = (key: string, value: string) => {
    setParams(prev => ({ ...prev, [key]: value }))
  }

  // 运行爬虫
  const handleRun = async () => {
    if (!selectedCrawler) return

    setIsRunning(true)
    setError('')

    try {
      const crawlerParams: RunCrawlerRequest = {}

      // 根据爬虫类型准备参数
      if (selectedCrawler === 'yahoo') {
        crawlerParams.symbol = params.symbol || 'AAPL'
      } else if (selectedCrawler === 'movies') {
        crawlerParams.max_pages = parseInt(params.max_pages || '1')
      } else if (selectedCrawler === 'jobs') {
        crawlerParams.search = params.search || ''
        crawlerParams.category = params.category || ''
      }

      const response = await crawlerApi.run(selectedCrawler, crawlerParams)
      
      // 通知父组件任务已创建
      onTaskCreated(response.task_id)
      
      // 清空表单
      setParams({})
    } catch (error: any) {
      const message = error.response?.data?.detail || '启动爬虫失败'
      setError(message)
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">爬虫控制面板</h2>

      {/* 错误提示 */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* 爬虫选择 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          选择爬虫
        </label>
        <select
          value={selectedCrawler}
          onChange={(e) => setSelectedCrawler(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {crawlers.map((crawler) => (
            <option key={crawler.name} value={crawler.name}>
              {crawler.display_name}
            </option>
          ))}
        </select>

        {/* 爬虫描述 */}
        {currentCrawler && (
          <p className="mt-2 text-sm text-gray-600">
            {currentCrawler.description}
          </p>
        )}
      </div>

      {/* 参数输入 */}
      {currentCrawler && (
        <div className="space-y-4 mb-6">
          {/* Yahoo 爬虫参数 */}
          {selectedCrawler === 'yahoo' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                股票代码 *
              </label>
              <input
                type="text"
                value={params.symbol || ''}
                onChange={(e) => handleParamChange('symbol', e.target.value)}
                placeholder="例如: AAPL, MSFT, GOOGL"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}

          {/* Movies 爬虫参数 */}
          {selectedCrawler === 'movies' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                页数（可选）
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={params.max_pages || '1'}
                onChange={(e) => handleParamChange('max_pages', e.target.value)}
                placeholder="1-10"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="mt-1 text-xs text-gray-500">每页25部电影，10页=250部</p>
            </div>
          )}

          {/* Jobs 爬虫参数 */}
          {selectedCrawler === 'jobs' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  搜索关键词（可选）
                </label>
                <input
                  type="text"
                  value={params.search || ''}
                  onChange={(e) => handleParamChange('search', e.target.value)}
                  placeholder="例如: python, data analyst"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  分类（可选）
                </label>
                <select
                  value={params.category || ''}
                  onChange={(e) => handleParamChange('category', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">全部</option>
                  <option value="software-dev">软件开发</option>
                  <option value="data">数据分析</option>
                  <option value="devops">DevOps</option>
                  <option value="design">设计</option>
                  <option value="marketing">市场营销</option>
                </select>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 运行按钮 */}
      <button
        onClick={handleRun}
        disabled={isRunning || !selectedCrawler}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isRunning ? (
          <>
            <Loader2 className="animate-spin mr-2" size={20} />
            启动中...
          </>
        ) : (
          <>
            <Play className="mr-2" size={20} />
            开始爬取
          </>
        )}
      </button>
    </div>
  )
}
