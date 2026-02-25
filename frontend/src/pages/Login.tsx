/**
 * Login page
 */
import React, { useMemo, useState } from 'react'
import { useNavigate, Link, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { LogIn, Loader2 } from 'lucide-react'

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { login, isLoading, error, clearError } = useAuthStore()
  
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    
    try {
      await login(username, password)
      // Check user role after login
      const { user } = useAuthStore.getState();
      if (user?.is_admin) {
        navigate('/admin')
      } else {
        navigate('/dashboard')
      }
    } catch (error) {
      // Error already handled in store
    }
  }

  const expiredMessage = useMemo(() => {
    return searchParams.get('reason') === 'expired'
      ? 'Session expired, please log in again'
      : null
  }, [searchParams])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="max-w-md w-full">
        {/* Logo and title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <LogIn className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Crawler Management Platform</h1>
          <p className="text-gray-600 mt-2">Log in to access your dashboard</p>
        </div>

        {/* Login form */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {expiredMessage && (
              <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-lg">
                {expiredMessage}
              </div>
            )}
            {/* Error alert */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="Enter username"
                autoComplete="username"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="Enter password"
                autoComplete="current-password"
              />
            </div>

            {/* Login button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={20} />
                  Logging in...
                </>
              ) : (
                <>
                  <LogIn className="mr-2" size={20} />
                  Log In
                </>
              )}
            </button>
          </form>

          {/* Register link */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
                Sign Up
              </Link>
            </p>
          </div>

          {/* Default credentials hint */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500 text-center mb-2">Default test credentials:</p>
            <div className="text-sm text-gray-600 text-center space-y-1">
              <p>Username: <code className="bg-gray-100 px-2 py-1 rounded">admin</code></p>
              <p>Password: <code className="bg-gray-100 px-2 py-1 rounded">admin123</code></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
