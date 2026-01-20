import React, { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { firecrawlApi } from '@/services/api'
import { FirecrawlFormat, FirecrawlScrapeResponse } from '@/types'
import { ArrowLeft, Sparkles } from 'lucide-react'

const DEFAULT_WEIBO_URL = 'https://s.weibo.com/top/summary?cate=realtimehot'

const formatOptions: { value: FirecrawlFormat; label: string }[] = [
  { value: 'markdown', label: 'Markdown' },
  { value: 'html', label: 'HTML' },
  { value: 'rawHtml', label: 'Raw HTML' },
  { value: 'screenshot', label: 'Screenshot' },
  { value: 'json', label: 'JSON' }
]

export const FirecrawlTestPage: React.FC = () => {
  const navigate = useNavigate()
  const [url, setUrl] = useState(DEFAULT_WEIBO_URL)
  const [formats, setFormats] = useState<FirecrawlFormat[]>(['markdown'])
  const [onlyMainContent, setOnlyMainContent] = useState(true)
  const [waitForMs, setWaitForMs] = useState('1200')
  const [timeoutMs, setTimeoutMs] = useState('30000')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<FirecrawlScrapeResponse | null>(null)

  const parsedWaitFor = useMemo(() => {
    const value = Number(waitForMs)
    return Number.isFinite(value) && value >= 0 ? value : undefined
  }, [waitForMs])

  const parsedTimeout = useMemo(() => {
    const value = Number(timeoutMs)
    return Number.isFinite(value) && value >= 1000 ? value : undefined
  }, [timeoutMs])

  const markdown = useMemo(() => {
    if (!result?.data) return ''
    const value = result.data['markdown']
    return typeof value === 'string' ? value : ''
  }, [result])

  const metadata = useMemo(() => {
    if (!result?.data) return null
    const value = result.data['metadata']
    return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : null
  }, [result])

  const toggleFormat = (value: FirecrawlFormat) => {
    setFormats((prev) => {
      if (prev.includes(value)) {
        return prev.filter((item) => item !== value)
      }
      return [...prev, value]
    })
  }

  const handleScrape = async () => {
    if (!url.trim()) {
      setError('请输入要抓取的 URL')
      return
    }
    if (formats.length === 0) {
      setError('至少选择一种输出格式')
      return
    }

    setIsLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await firecrawlApi.scrape({
        url,
        formats,
        only_main_content: onlyMainContent,
        wait_for: parsedWaitFor,
        timeout_ms: parsedTimeout
      })
      setResult(response)
      if (!response.success) {
        setError(response.error || 'Firecrawl 返回失败')
      }
    } catch (error) {
      const message =
        error instanceof Error && error.message
          ? error.message
          : '请求失败，请检查 Firecrawl 配置或网络'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setUrl(DEFAULT_WEIBO_URL)
    setFormats(['markdown'])
    setOnlyMainContent(true)
    setWaitForMs('1200')
    setTimeoutMs('30000')
    setError(null)
    setResult(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft size={18} />
                返回
              </button>
              <h1 className="text-xl font-bold text-gray-900">Firecrawl 测试</h1>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Sparkles size={16} />
              Weibo 热搜测试页
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">抓取 URL</label>
            <input
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="https://s.weibo.com/top/summary?cate=realtimehot"
            />
            <p className="text-xs text-gray-500 mt-2">默认使用微博热搜公开页</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">输出格式</label>
            <div className="flex flex-wrap gap-3">
              {formatOptions.map((option) => (
                <label key={option.value} className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={formats.includes(option.value)}
                    onChange={() => toggleFormat(option.value)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={onlyMainContent}
                onChange={(event) => setOnlyMainContent(event.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              仅主内容
            </label>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">等待加载 (ms)</label>
              <input
                value={waitForMs}
                onChange={(event) => setWaitForMs(event.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">超时 (ms)</label>
              <input
                value={timeoutMs}
                onChange={(event) => setTimeoutMs(event.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleScrape}
              disabled={isLoading}
              className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-60"
            >
              {isLoading ? '抓取中...' : '开始抓取'}
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              重置
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {result && (
            <div className="space-y-4">
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm text-gray-700">
                <div>success: {String(result.success)}</div>
                {metadata?.title && <div>title: {String(metadata.title)}</div>}
                {metadata?.sourceURL && <div>source: {String(metadata.sourceURL)}</div>}
                {metadata?.statusCode && <div>statusCode: {String(metadata.statusCode)}</div>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Markdown 预览</label>
                <textarea
                  readOnly
                  value={markdown}
                  className="w-full h-64 border border-gray-300 rounded-lg p-3 text-sm font-mono"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">完整响应</label>
                <textarea
                  readOnly
                  value={JSON.stringify(result, null, 2)}
                  className="w-full h-64 border border-gray-300 rounded-lg p-3 text-sm font-mono"
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FirecrawlTestPage
