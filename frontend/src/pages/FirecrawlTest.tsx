import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { firecrawlApi } from '@/services/api'
import { FirecrawlFormat, FirecrawlScrapeResponse } from '@/types'
import { ArrowLeft, Sparkles } from 'lucide-react'

const DEFAULT_WEIBO_URL = 'https://s.weibo.com/top/summary?cate=realtimehot'
const COOKIE_STORAGE_KEY = 'firecrawl_weibo_cookie_list'

type SavedCookie = {
  id: string
  name: string
  value: string
  updated_at: string
}

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
  const [cookieName, setCookieName] = useState('')
  const [savedCookies, setSavedCookies] = useState<SavedCookie[]>([])
  const [selectedCookieId, setSelectedCookieId] = useState('')
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const hasLoadedCookiesRef = useRef(false)
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

  useEffect(() => {
    try {
      const raw = localStorage.getItem(COOKIE_STORAGE_KEY)
      if (!raw) return
      const parsed = JSON.parse(raw) as SavedCookie[]
      if (Array.isArray(parsed)) {
        setSavedCookies(parsed)
      }
    } catch (error) {
      console.warn('Failed to load cookie list', error)
    } finally {
      hasLoadedCookiesRef.current = true
    }
  }, [])

  useEffect(() => {
    if (!hasLoadedCookiesRef.current) return
    localStorage.setItem(COOKIE_STORAGE_KEY, JSON.stringify(savedCookies))
  }, [savedCookies])

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
      setError('Please enter a URL to scrape')
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
        setError(response.error || 'Firecrawl returned failure')
      }
    } catch (error) {
      const message =
        error instanceof Error && error.message
          ? error.message
          : 'Request failed, please check Firecrawl config or network'
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
    setCookieName('')
    setSelectedCookieId('')
    setError(null)
    setResult(null)
  }

  const handleDownload = async () => {
    if (!result) return
    if (!result.data) {
      setError('Current result is empty, cannot download')
      return
    }
    const value = result.data[format]
    if (typeof value !== 'string') {
      setError('Current result does not contain the selected download format')
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
        setError('Current result does not contain screenshot data')
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
          console.error('Screenshot base64 decode failed', decodeError)
          setError('Screenshot data format incorrect, cannot decode for download')
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

  const handleSelectCookie = (id: string) => {
    setSelectedCookieId(id)
    const selected = savedCookies.find((item) => item.id === id)
    if (selected) {
      setCookie(selected.value)
      setCookieName(selected.name)
    }
  }

  const handleSaveCookie = () => {
    const name = cookieName.trim()
    const value = cookie.trim()
    if (!name || !value) {
      setError('Please fill in Cookie name and content before saving')
      return
    }
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`
    const entry: SavedCookie = {
      id,
      name,
      value,
      updated_at: new Date().toISOString()
    }
    setSavedCookies((prev) => [entry, ...prev])
    setSelectedCookieId(id)
  }

  const handleUpdateCookie = () => {
    const value = cookie.trim()
    if (!selectedCookieId) {
      setError('Please select a saved Cookie first')
      return
    }
    if (!value) {
      setError('Current Cookie is empty, cannot update')
      return
    }
    setSavedCookies((prev) =>
      prev.map((item) =>
        item.id === selectedCookieId
          ? { ...item, value, updated_at: new Date().toISOString() }
          : item
      )
    )
  }

  const handleDeleteCookie = () => {
    if (!selectedCookieId) {
      setError('Please select a saved Cookie first')
      return
    }
    setSavedCookies((prev) => prev.filter((item) => item.id !== selectedCookieId))
    setSelectedCookieId('')
    setCookieName('')
  }

  const handleExportCookies = () => {
    if (savedCookies.length === 0) {
      setError('No Cookie available for export')
      return
    }
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const fileName = `firecrawl-cookies-${timestamp}.json`
    const blob = new Blob([JSON.stringify(savedCookies, null, 2)], {
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

  const handleImportCookies = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const parsed = JSON.parse(String(reader.result)) as SavedCookie[]
        if (!Array.isArray(parsed)) {
          throw new Error('Cookie file format is incorrect')
        }
        const normalized = parsed
          .filter((item) => item?.name && item?.value)
          .map((item) => ({
            id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
            name: String(item.name),
            value: String(item.value),
            updated_at: item.updated_at || new Date().toISOString()
          }))
        if (normalized.length === 0) {
          setError('No valid Cookie found in file')
          return
        }
        setSavedCookies((prev) => [...normalized, ...prev])
        setError(null)
      } catch (error) {
        setError(error instanceof Error ? error.message : 'Import failed')
      } finally {
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }
    }
    reader.readAsText(file)
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
                Back
              </button>
              <h1 className="text-xl font-bold text-gray-900">Firecrawl Test</h1>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Sparkles size={16} />
              Weibo Hot Search Test Page
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Scrape URL</label>
            <input
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="https://s.weibo.com/top/summary?cate=realtimehot"
            />
            <p className="text-xs text-gray-500 mt-2">Defaults to Weibo Hot Search public page</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Output Format</label>
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
            <label className="block text-sm font-medium text-gray-700 mb-2">Login Cookie (optional)</label>
            <textarea
              value={cookie}
              onChange={(event) => setCookie(event.target.value)}
              className="w-full h-28 border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono"
              placeholder="Copy Cookie header from browser Network tab (paste in full)"
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Cookie Name</label>
                <input
                  value={cookieName}
                  onChange={(event) => setCookieName(event.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  placeholder="e.g.: my-weibo-account"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Saved Cookies</label>
                <select
                  value={selectedCookieId}
                  onChange={(event) => handleSelectCookie(event.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">Select</option>
                  {savedCookies.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-end gap-2">
                <button
                  onClick={handleSaveCookie}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                >
                  Save as New
                </button>
                <button
                  onClick={handleUpdateCookie}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                >
                  Update Selected
                </button>
                <button
                  onClick={handleDeleteCookie}
                  className="px-3 py-2 border border-red-200 rounded-lg text-sm text-red-600 hover:bg-red-50"
                >
                  Delete
                </button>
                <button
                  onClick={handleExportCookies}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                >
                  Export
                </button>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                >
                  Import
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/json"
                  onChange={handleImportCookies}
                  className="hidden"
                />
              </div>
            </div>
            <div className="text-xs text-gray-500 mt-2 space-y-1">
              <div>How to get: Login to target site → F12 → Network → Select page request → Request Headers → Cookie</div>
              <div>Cookies are saved to local browser (localStorage) only, not uploaded to server.</div>
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
              Main Content Only
            </label>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Wait for Load (ms)</label>
              <input
                value={waitForMs}
                onChange={(event) => setWaitForMs(event.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Timeout (ms)</label>
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
              {isLoading ? 'Scraping...' : 'Start Scraping'}
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Reset
            </button>
            <button
              onClick={handleDownload}
              disabled={!result}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-60"
            >
              Download Result
            </button>
            <button
              onClick={handleDownloadJson}
              disabled={!result}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-60"
            >
              Download JSON
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
                <label className="block text-sm font-medium text-gray-700 mb-2">Content Preview</label>
                {format === 'screenshot' ? (
                  screenshotPreview ? (
                    <img
                      src={screenshotPreview}
                      alt="Screenshot preview"
                      className="max-h-64 border border-gray-300 rounded-lg"
                    />
                  ) : (
                    <div className="text-sm text-gray-500">Current result does not contain screenshot data.</div>
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
                <label className="block text-sm font-medium text-gray-700 mb-2">Full Response</label>
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
