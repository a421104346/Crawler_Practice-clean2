/**
 * Main application component
 * Route configuration and global layout
 */
import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { LoginPage } from '@/pages/Login'
import { RegisterPage } from '@/pages/Register'
import { Dashboard } from '@/pages/Dashboard'
import { HistoryPage } from '@/pages/History'
import { FirecrawlTestPage } from '@/pages/FirecrawlTest'
import { FirecrawlHotRankPage } from '@/pages/FirecrawlHotRank'
import AdminDashboard from '@/pages/AdminDashboard'
import { isDemoModeEnabled } from '@/services/api'

// Protected route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user, isLoading } = useAuthStore()
  
  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  // If admin, prevent access to regular user pages, redirect to Admin Dashboard
  if (user?.is_admin) {
    return <Navigate to="/admin" replace />
  }
  
  return <>{children}</>
}

// Root path redirect component
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

// Admin route component
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

  // Fetch user info on app startup
  useEffect(() => {
    if (isAuthenticated) {
      fetchUser()
    }
  }, [isAuthenticated, fetchUser])

  return (
    <BrowserRouter>
      {isDemoModeEnabled && (
        <div className="fixed right-4 top-4 z-50 rounded-full border border-amber-300 bg-amber-100 px-4 py-1 text-xs font-semibold uppercase tracking-wide text-amber-800 shadow-sm">
          Demo Mode
        </div>
      )}
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected routes */}
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
        <Route
          path="/firecrawl"
          element={
            <ProtectedRoute>
              <FirecrawlTestPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/firecrawl/hot-rank1"
          element={
            <ProtectedRoute>
              <FirecrawlHotRankPage />
            </ProtectedRoute>
          }
        />

        {/* Default route */}
        <Route path="/" element={<HomeRedirect />} />
        
        {/* 404 route - redirect based on role */}
        <Route path="*" element={<HomeRedirect />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
