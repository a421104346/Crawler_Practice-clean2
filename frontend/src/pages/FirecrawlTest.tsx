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
  { value: 'screenshot', label: 'Screenshot' }
]

export const FirecrawlTestPage: React.FC = () => {
  const navigate = useNavigate()
  const [url, setUrl] = useState(DEFAULT_WEIBO_URL)
  const [format, setFormat] = useState<FirecrawlFormat>('markdown')
  const [onlyMainContent, setOnlyMainContent] = useState(true)
  const [waitForMs, setWaitForMs] = useState('1200')
  const [timeoutMs, setTimeoutMs] = useState('30000')
  const [cookie, setCookie] = useState('')
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

  const previewText = useMemo(() => {
    if (!result?.data) return ''
    if (format === 'screenshot') return ''
    const value = result.data[format]
    return typeof value === 'string' ? value : ''
  }, [result, format])

  const screenshotPreview = useMemo(() => {
    if (!result?.data || format !== 'screenshot') return ''
    const value = result.data['screenshot']
    if (typeof value !== 'string' || !value.trim()) return ''
    if (value.startsWith('data:image') || value.startsWith('http')) {
      return value
    }
    return `data:image/png;base64,${value}`
  }, [result, format])

  const metadata = useMemo(() => {
    if (!result?.data) return null
    const value = result.data['metadata']
    return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : null
  }, [result])

  const handleScrape = async () => {
    if (!url.trim()) {
      setError('请输入要抓取的 URL')
      return
    }

    setIsLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await firecrawlApi.scrape({
        url,
        formats: [format],
        only_main_content: onlyMainContent,
        wait_for: parsedWaitFor,
        timeout_ms: parsedTimeout,
        cookie: cookie || undefined
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
    setFormat('markdown')
    setOnlyMainContent(true)
    setWaitForMs('1200')
    setTimeoutMs('30000')
    setCookie('')
    setError(null)
    setResult(null)
  }

  const handleDownload = async () => {
    if (!result) return
    if (!result.data) {
      setError('当前结果为空，无法下载')
      return
    }
    const value = result.data[format]
    if (typeof value !== 'string') {
      setError('当前结果未包含所选下载格式')
      return
    }
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const extensionMap: Record<FirecrawlFormat, string> = {
      markdown: 'md',
      html: 'html',
      rawHtml: 'html',
      screenshot: 'png',
      json: 'json'
    }
    const fileName = `firecrawl-${timestamp}.${extensionMap[format]}`
    let downloadUrl = ''
    let blob: Blob | null = null

    if (format === 'screenshot') {
      if (!value) {
        setError('当前结果未包含截图数据')
        return
      }
      if (value.startsWith('data:image') || value.startsWith('http')) {
        downloadUrl = value
      } else {
        try {
          const binary = atob(value)
          const bytes = new Uint8Array(binary.length)
          for (let i = 0; i < binary.length; i += 1) {
            bytes[i] = binary.charCodeAt(i)
          }
          blob = new Blob([bytes], { type: 'image/png' })
        } catch (decodeError) {
          console.error('截图 base64 解码失败', decodeError)
          setError('截图数据格式不正确，无法解码下载')
          return
        }
      }
    } else {
      blob = new Blob([value], { type: 'text/plain;charset=utf-8' })
    }

    if (blob) {
      downloadUrl = URL.createObjectURL(blob)
    }

    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = fileName
    if (downloadUrl.startsWith('http')) {
      link.target = '_blank'
      link.rel = 'noreferrer'
    }
    document.body.appendChild(link)
    link.click()
    link.remove()
    if (blob) {
      URL.revokeObjectURL(downloadUrl)
    }
  }

  const handleDownloadJson = () => {
    if (!result) return
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const fileName = `firecrawl-${timestamp}.json`
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: 'application/json;charset=utf-8'
    })
    const downloadUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(downloadUrl)
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
                    type="radio"
                    name="output-format"
                    checked={format === option.value}
                    onChange={() => setFormat(option.value)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">登录 Cookie（可选）</label>
            <textarea
              value={cookie}
              onChange={(event) => setCookie(event.target.value)}
              className="w-full h-28 border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono"
              placeholder="从浏览器 Network 请求里复制 Cookie 头（完整粘贴）"
            />
            <div className="text-xs text-gray-500 mt-2 space-y-1">
              <div>获取方式：登录目标站点 → F12 → Network → 选中页面请求 → Request Headers → Cookie</div>
              <div>仅用于当前请求，不会保存到本地。</div>
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
            <button
              onClick={handleDownload}
              disabled={!result}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-60"
            >
              下载结果
            </button>
            <button
              onClick={handleDownloadJson}
              disabled={!result}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-60"
            >
              下载 JSON
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
                <label className="block text-sm font-medium text-gray-700 mb-2">内容预览</label>
                {format === 'screenshot' ? (
                  screenshotPreview ? (
                    <img
                      src={screenshotPreview}
                      alt="Screenshot preview"
                      className="max-h-64 border border-gray-300 rounded-lg"
                    />
                  ) : (
                    <div className="text-sm text-gray-500">当前结果未包含截图数据。</div>
                  )
                ) : (
                  <textarea
                    readOnly
                    value={previewText}
                    className="w-full h-64 border border-gray-300 rounded-lg p-3 text-sm font-mono"
                  />
                )}
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
