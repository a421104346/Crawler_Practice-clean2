/**
 * 注册页面
 */
import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { UserPlus, Loader2 } from 'lucide-react'

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { register, isLoading, error, clearError } = useAuthStore()
  
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [localError, setLocalError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    setLocalError('')

    // 验证密码
    if (password !== confirmPassword) {
      setLocalError('两次输入的密码不一致')
      return
    }

    if (password.length < 6) {
      setLocalError('密码长度至少为 6 位')
      return
    }

    try {
      await register(username, email, password)
      navigate('/dashboard')
    } catch (error) {
      // 错误已经在 store 中处理
    }
  }

  const displayError = error || localError

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="max-w-md w-full">
        {/* Logo 和标题 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">创建账号</h1>
          <p className="text-gray-600 mt-2">注册新账号以开始使用</p>
        </div>

        {/* 注册表单 */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 错误提示 */}
            {displayError && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {displayError}
              </div>
            )}

            {/* 用户名 */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                用户名 *
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                minLength={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="至少 3 个字符"
                autoComplete="username"
              />
            </div>

            {/* 邮箱 */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                邮箱（可选）
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="your@email.com"
                autoComplete="email"
              />
            </div>

            {/* 密码 */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                密码 *
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="至少 6 个字符"
                autoComplete="new-password"
              />
            </div>

            {/* 确认密码 */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                确认密码 *
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="再次输入密码"
                autoComplete="new-password"
              />
            </div>

            {/* 注册按钮 */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={20} />
                  注册中...
                </>
              ) : (
                <>
                  <UserPlus className="mr-2" size={20} />
                  注册
                </>
              )}
            </button>
          </form>

          {/* 登录链接 */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              已有账号？{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                立即登录
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
