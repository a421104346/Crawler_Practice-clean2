/**
 * Crawler control panel component
 * For selecting crawler type and configuring parameters
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

  // Load crawler list
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

  // Get selected crawler info
  const currentCrawler = crawlers.find(c => c.name === selectedCrawler)

  // Handle parameter change
  const handleParamChange = (key: string, value: string) => {
    setParams(prev => ({ ...prev, [key]: value }))
  }

  // Run crawler
  const handleRun = async () => {
    if (!selectedCrawler) return

    setIsRunning(true)
    setError('')

    try {
      const crawlerParams: RunCrawlerRequest = {}

      // Prepare parameters by crawler type
      if (selectedCrawler === 'yahoo') {
        crawlerParams.symbol = params.symbol || 'AAPL'
      } else if (selectedCrawler === 'movies') {
        const pagesInput = params.max_pages
        let pages = 1
        if (pagesInput) {
            pages = parseInt(pagesInput, 10)
            if (isNaN(pages)) pages = 1
        }
        // console.log('Sending params:', { ...params, max_pages: pages })
        crawlerParams.max_pages = pages
      } else if (selectedCrawler === 'jobs') {
        crawlerParams.search = params.search || ''
        crawlerParams.category = params.category || ''
      }

      const response = await crawlerApi.run(selectedCrawler, crawlerParams)
      
      // Notify parent that task was created
      onTaskCreated(response.task_id)
      
      // Clear form
      setParams({})
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to start crawler'
      setError(message)
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Crawler Control Panel</h2>

      {/* Error alert */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Crawler selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Crawler
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

        {/* Crawler description */}
        {currentCrawler && (
          <p className="mt-2 text-sm text-gray-600">
            {currentCrawler.description}
          </p>
        )}
      </div>

      {/* Parameter inputs */}
      {currentCrawler && (
        <div className="space-y-4 mb-6">
          {/* Yahoo crawler parameters */}
          {selectedCrawler === 'yahoo' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stock Symbol *
              </label>
              <input
                type="text"
                value={params.symbol || ''}
                onChange={(e) => handleParamChange('symbol', e.target.value)}
                placeholder="e.g. AAPL, MSFT, GOOGL"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}

          {/* Movies crawler parameters */}
          {selectedCrawler === 'movies' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Pages (optional)
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={params.max_pages || ''}
                onChange={(e) => handleParamChange('max_pages', e.target.value)}
                placeholder="Default: 1"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="mt-1 text-xs text-gray-500">25 movies per page, 10 pages = 250 movies</p>
            </div>
          )}

          {/* Jobs crawler parameters */}
          {selectedCrawler === 'jobs' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search Keywords (optional)
                </label>
                <input
                  type="text"
                  value={params.search || ''}
                  onChange={(e) => handleParamChange('search', e.target.value)}
                  placeholder="e.g. python, data analyst"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category (optional)
                </label>
                <select
                  value={params.category || ''}
                  onChange={(e) => handleParamChange('category', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All</option>
                  <option value="software-dev">Software Dev</option>
                  <option value="data">Data</option>
                  <option value="devops">DevOps</option>
                  <option value="design">Design</option>
                  <option value="marketing">Marketing</option>
                </select>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Run button */}
      <button
        onClick={handleRun}
        disabled={isRunning || !selectedCrawler}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isRunning ? (
          <>
            <Loader2 className="animate-spin mr-2" size={20} />
            Starting...
          </>
        ) : (
          <>
            <Play className="mr-2" size={20} />
            Start Crawling
          </>
        )}
      </button>
    </div>
  )
}
