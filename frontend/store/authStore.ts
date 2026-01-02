import { create } from 'zustand'
import { authAPI } from '@/lib/api'

interface User {
  id: string
  email: string
  subscription_tier: string
  credits: number
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

const getInitialToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: getInitialToken(),
  isAuthenticated: !!getInitialToken(),
  
  login: async (email: string, password: string) => {
    const data = await authAPI.login(email, password)
    const token = data.access_token
    if (!token) {
      throw new Error('No token received from login')
    }
    localStorage.setItem('access_token', token)
    set({ token, isAuthenticated: true })
    try {
      await get().fetchUser()
    } catch (error) {
      // If fetchUser fails, still keep the token
      console.error('Failed to fetch user after login:', error)
    }
  },
  
  register: async (email: string, password: string) => {
    await authAPI.register(email, password)
    await get().login(email, password)
  },
  
  logout: () => {
    localStorage.removeItem('access_token')
    set({ user: null, token: null, isAuthenticated: false })
  },
  
  fetchUser: async () => {
    try {
      const user = await authAPI.getMe()
      const token = localStorage.getItem('access_token')
      set({ user, isAuthenticated: true, token })
    } catch (error: any) {
      // If 401, token is expired - clear it
      if (error.response?.status === 401) {
        localStorage.removeItem('access_token')
        set({ user: null, isAuthenticated: false, token: null })
      }
      console.error('Failed to fetch user:', error)
    }
  },
}))




