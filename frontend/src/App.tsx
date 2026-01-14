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
import AdminDashboard from '@/pages/AdminDashboard'

// 受保护的路由组件
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user, isLoading } = useAuthStore()
  
  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  // 如果是管理员，禁止访问普通用户页面，重定向到 Admin Dashboard
  if (user?.is_admin) {
    return <Navigate to="/admin" replace />
  }
  
  return <>{children}</>
}

// 根路径重定向组件
const HomeRedirect: React.FC = () => {
  const { isAuthenticated, user, isLoading } = useAuthStore()
  
  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (user?.is_admin) {
    return <Navigate to="/admin" replace />
  }

  return <Navigate to="/dashboard" replace />
}

// 管理员路由组件
const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  if (!user?.is_admin) {
    return <Navigate to="/dashboard" replace />
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
          path="/admin"
          element={
            <AdminRoute>
              <AdminDashboard />
            </AdminRoute>
          }
        />
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
        <Route path="/" element={<HomeRedirect />} />
        
        {/* 404 路由 - 根据角色重定向 */}
        <Route path="*" element={<HomeRedirect />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
