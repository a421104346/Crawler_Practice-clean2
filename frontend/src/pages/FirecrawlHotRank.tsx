import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { firecrawlApi } from '@/services/api'
import {
  FirecrawlWeiboHotRankResponse,
  FirecrawlWeiboHotRankResult,
  WeiboHotRankPost
} from '@/types'
import { ArrowLeft, Flame } from 'lucide-react'

const DEFAULT_PAGES = '5'
const COOKIE_STORAGE_KEY = 'firecrawl_weibo_cookie_list'

const formatContent = (content: string) => content.replace(/\s+/g, ' ').trim()

type SavedCookie = {
  id: string
  name: string
  value: string
  updated_at: string
}

export const FirecrawlHotRankPage: React.FC = () => {
  const navigate = useNavigate()
  const [pages, setPages] = useState(DEFAULT_PAGES)
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
  const [result, setResult] = useState<FirecrawlWeiboHotRankResponse | null>(null)

  const parsedPages = useMemo(() => {
    const value = Number(pages)
    if (!Number.isFinite(value)) return 5
    return Math.min(5, Math.max(1, Math.floor(value)))
  }, [pages])

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

  const handleScrape = async () => {
    setIsLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await firecrawlApi.weiboHotRank1({
        pages: parsedPages,
        wait_for: parsedWaitFor,
        timeout_ms: parsedTimeout,
        cookie: cookie || undefined
      })
      setResult(response)
      if (!response.success) {
        setError(response.error || '抓取失败')
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
    setPages(DEFAULT_PAGES)
    setWaitForMs('1200')
    setTimeoutMs('30000')
    setCookie('')
    setSelectedCookieId('')
    setCookieName('')
    setError(null)
    setResult(null)
  }

  const handleDownloadJson = () => {
    if (!result) return
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const fileName = `firecrawl-hot-rank1-${timestamp}.json`
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
      setError('请填写 Cookie 名称和内容再保存')
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
      setError('请先选择一个已保存的 Cookie')
      return
    }
    if (!value) {
      setError('当前 Cookie 为空，无法更新')
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
      setError('请先选择一个已保存的 Cookie')
      return
    }
    setSavedCookies((prev) => prev.filter((item) => item.id !== selectedCookieId))
    setSelectedCookieId('')
    setCookieName('')
  }

  const handleExportCookies = () => {
    if (savedCookies.length === 0) {
      setError('当前没有可导出的 Cookie')
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
          throw new Error('Cookie 文件格式不正确')
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
          setError('未在文件中找到有效 Cookie')
          return
        }
        setSavedCookies((prev) => [...normalized, ...prev])
        setError(null)
      } catch (error) {
        setError(error instanceof Error ? error.message : '导入失败')
      } finally {
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }
    }
    reader.readAsText(file)
  }

  const resultData: FirecrawlWeiboHotRankResult | null = result?.data || null
  const posts: WeiboHotRankPost[] = resultData?.posts || []

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
              <h1 className="text-xl font-bold text-gray-900">Firecrawl 热搜 Rank1</h1>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Flame size={16} />
              微博热搜话题抓取
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">抓取页数</label>
              <input
                value={pages}
                onChange={(event) => setPages(event.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">最大 5 页，默认抓取前 5 页</p>
            </div>

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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">登录 Cookie（可选）</label>
            <textarea
              value={cookie}
              onChange={(event) => setCookie(event.target.value)}
              className="w-full h-28 border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono"
              placeholder="从浏览器 Network 请求里复制 Cookie 头（完整粘贴）"
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Cookie 名称</label>
                <input
                  value={cookieName}
                  onChange={(event) => setCookieName(event.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  placeholder="例如：我的微博账号"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">已保存 Cookie</label>
                <select
                  value={selectedCookieId}
                  onChange={(event) => handleSelectCookie(event.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">请选择</option>
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
                  保存为新
                </button>
                <button
                  onClick={handleUpdateCookie}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                >
                  更新选中
                </button>
                <button
                  onClick={handleDeleteCookie}
                  className="px-3 py-2 border border-red-200 rounded-lg text-sm text-red-600 hover:bg-red-50"
                >
                  删除
                </button>
                <button
                  onClick={handleExportCookies}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                >
                  导出
                </button>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                >
                  导入
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
              <div>如遇反爬或登录墙，可以填 Cookie 提升成功率。</div>
              <div>Cookie 仅保存到本地浏览器（localStorage），不会上传服务器。</div>
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

          {resultData && (
            <div className="space-y-4">
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm text-gray-700">
                <div>话题：{resultData.topic_title}</div>
                <div>
                  链接：
                  <a
                    href={resultData.topic_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-600 hover:text-blue-700 ml-2"
                  >
                    打开话题页
                  </a>
                </div>
                <div>抓取页数：{resultData.pages}</div>
                <div>帖子数量：{resultData.total_posts}</div>
              </div>

              {posts.length === 0 ? (
                <div className="text-sm text-gray-500">当前未抓取到帖子内容。</div>
              ) : (
                <div className="space-y-3">
                  {posts.map((post, index) => (
                    <div
                      key={`${post.username}-${index}`}
                      className="border border-gray-200 rounded-lg p-4 space-y-2"
                    >
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <span className="font-medium text-gray-900">{post.username}</span>
                        {post.user_link && (
                          <a
                            href={post.user_link}
                            target="_blank"
                            rel="noreferrer"
                            className="text-blue-600 hover:text-blue-700 text-xs"
                          >
                            主页
                          </a>
                        )}
                      </div>
                      <div className="text-sm text-gray-700 leading-relaxed">
                        {formatContent(post.content)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FirecrawlHotRankPage
