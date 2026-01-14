/**
 * 认证状态管理
 * 使用 Zustand 进行轻量级状态管理
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { authApi } from '@/services/api'

interface AuthState {
  // 状态
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // 操作
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  fetchUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      user: null,
      token: localStorage.getItem('access_token'),
      isAuthenticated: !!localStorage.getItem('access_token'),
      isLoading: false,
      error: null,

      // 登录
      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          // Send request with username/password JSON
          const response = await authApi.login(username, password)
          
          // 保存 token
          localStorage.setItem('access_token', response.access_token)
          
          set({
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          })

          // 获取用户信息
          await get().fetchUser()
        } catch (error: any) {
          console.error("Login failed:", error);
          const message = error.response?.data?.detail || '登录失败'
          set({
            error: message,
            isLoading: false,
            isAuthenticated: false,
          })
          throw error
        }
      },

      // 注册
      register: async (username: string, email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          await authApi.register(username, email, password)
          
          // 注册成功后自动登录
          await get().login(username, password)
        } catch (error: any) {
          const message = error.response?.data?.detail || '注册失败'
          set({
            error: message,
            isLoading: false,
          })
          throw error
        }
      },

      // 登出
      logout: async () => {
        try {
          await authApi.logout()
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          localStorage.removeItem('access_token')
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            error: null,
          })
        }
      },

      // 获取用户信息
      fetchUser: async () => {
        if (!get().token) return

        set({ isLoading: true })
        try {
          const user = await authApi.getCurrentUser()
          set({ user, isLoading: false })
        } catch (error) {
          console.error('Fetch user error:', error)
          set({ isLoading: false })
          // Token 可能已过期，清除状态
          get().logout()
        }
      },

      // 清除错误
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
