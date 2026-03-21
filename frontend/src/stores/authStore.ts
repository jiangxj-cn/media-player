import { create } from 'zustand'
import { api, getAuthToken, setAuthToken, clearAuth } from '../utils/api'

export interface User {
  id: string
  username: string
  created_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  login: (username: string, password: string) => Promise<void>
  register: (username: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  clearError: () => void
}

interface LoginResponse {
  token: string
  user: User
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: getAuthToken(),
  isAuthenticated: !!getAuthToken(),
  isLoading: false,
  error: null,
  
  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await api.post<LoginResponse>('/api/auth/login', 
        { username, password },
        { skipAuth: true }
      )
      
      setAuthToken(response.token)
      set({
        user: response.user,
        token: response.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
      
      // Store user info in localStorage for quick access
      localStorage.setItem('auth_user', JSON.stringify(response.user))
    } catch (err) {
      const message = err instanceof Error ? err.message : '登录失败'
      set({ isLoading: false, error: message })
      throw err
    }
  },
  
  register: async (username: string, password: string) => {
    set({ isLoading: true, error: null })
    
    try {
      await api.post('/api/auth/register', 
        { username, password },
        { skipAuth: true }
      )
      
      // Auto login after registration
      await get().login(username, password)
    } catch (err) {
      const message = err instanceof Error ? err.message : '注册失败'
      set({ isLoading: false, error: message })
      throw err
    }
  },
  
  logout: () => {
    clearAuth()
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    })
  },
  
  checkAuth: async () => {
    const token = getAuthToken()
    if (!token) {
      set({ isAuthenticated: false, user: null, token: null })
      return
    }
    
    // Try to get stored user first
    const storedUser = localStorage.getItem('auth_user')
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser)
        set({ user, token, isAuthenticated: true })
      } catch {
        // Invalid stored user, clear it
        localStorage.removeItem('auth_user')
      }
    }
    
    // Verify token with server
    try {
      const user = await api.get<User>('/api/auth/profile')
      set({ user, token, isAuthenticated: true })
      localStorage.setItem('auth_user', JSON.stringify(user))
    } catch {
      // Token is invalid, clear auth
      clearAuth()
      set({ user: null, token: null, isAuthenticated: false })
    }
  },
  
  clearError: () => set({ error: null }),
}))