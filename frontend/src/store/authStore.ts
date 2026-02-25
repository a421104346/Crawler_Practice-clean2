/**
 * Auth state management
 * Lightweight state management with Zustand
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { authApi } from '@/services/api'

const isTokenExpired = (token: string): boolean => {
  try {
    const [, payload] = token.split('.')
    if (!payload) return true
    const decoded = JSON.parse(atob(payload))
    const exp = typeof decoded?.exp === 'number' ? decoded.exp * 1000 : 0
    return !exp || Date.now() >= exp
  } catch {
    return true
  }
}

interface AuthState {
  // State
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  fetchUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: localStorage.getItem('access_token'),
      isAuthenticated: !!localStorage.getItem('access_token'),
      isLoading: false,
      error: null,

      // Login
      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          // Send request with username/password JSON
          const response = await authApi.login(username, password)
          
          // Save token
          localStorage.setItem('access_token', response.access_token)
          
          set({
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          })

          // Fetch user info
          await get().fetchUser()
        } catch (error: any) {
          console.error("Login failed:", error);
          const message = error.response?.data?.detail || 'Login failed'
          set({
            error: message,
            isLoading: false,
            isAuthenticated: false,
          })
          throw error
        }
      },

      // Register
      register: async (username: string, email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          await authApi.register(username, email, password)
          
          // Auto-login after successful registration
          await get().login(username, password)
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Registration failed'
          set({
            error: message,
            isLoading: false,
          })
          throw error
        }
      },

      // Logout
      logout: async () => {
        try {
          if (get().token) {
            await authApi.logout()
          }
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

      // Fetch user info
      fetchUser: async () => {
        const token = get().token
        if (!token) return
        if (isTokenExpired(token)) {
          localStorage.removeItem('access_token')
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          })
          return
        }

        set({ isLoading: true })
        try {
          const user = await authApi.getCurrentUser()
          set({ user, isLoading: false })
        } catch (error) {
          console.error('Fetch user error:', error)
          localStorage.removeItem('access_token')
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          })
        }
      },

      // Clear error
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
