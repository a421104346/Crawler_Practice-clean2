/**
 * 主应用组件
 * 路由配置和全局布局
 */
import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { LoginPage } from '@/pages/Login'
import { RegisterPage } from '@/pages/Register'
import { Dashboard } from '@/pages/Dashboard'
import { HistoryPage } from '@/pages/History'

// 受保护的路由组件
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

export const App: React.FC = () => {
  const { fetchUser, isAuthenticated } = useAuthStore()

  // 应用启动时获取用户信息
  useEffect(() => {
    if (isAuthenticated) {
      fetchUser()
    }
  }, [isAuthenticated, fetchUser])

  return (
    <BrowserRouter>
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* 受保护的路由 */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <HistoryPage />
            </ProtectedRoute>
          }
        />

        {/* 默认路由 */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        {/* 404 路由 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
