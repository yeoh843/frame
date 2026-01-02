import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  // Axios automatically sets Content-Type based on data:
  // - Objects → application/json
  // - FormData → multipart/form-data with boundary
  // - URLSearchParams → application/x-www-form-urlencoded
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // For FormData, don't set Content-Type - axios will set it with boundary automatically
  if (config.data instanceof FormData) {
    // Axios automatically sets Content-Type for FormData, so remove any preset
    delete config.headers['Content-Type']
  }
  return config
})

// Handle 401 errors globally - clear expired token
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only handle 401 if we have a response (server responded)
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      // Don't redirect here - let the component handle it
      // Just clear the token and let the error propagate
    }
    // Always reject the error so components can handle it
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: async (email: string, password: string) => {
    try {
      const response = await api.post('/api/v1/auth/register', { email, password }, {
        headers: { 'Content-Type': 'application/json' }
      })
      return response.data
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Registration failed'
      throw new Error(message)
    }
  },
  
  login: async (email: string, password: string) => {
    try {
      // OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
      const params = new URLSearchParams()
      params.append('username', email)
      params.append('password', password)
      const response = await api.post('/api/v1/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      return response.data
    } catch (error: any) {
      console.error('Login error:', error)
      console.error('Error response:', error.response?.data)
      console.error('Error status:', error.response?.status)
      const message = error.response?.data?.detail || error.message || 'Login failed'
      throw new Error(message)
    }
  },
  
  getMe: async () => {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  },
}

export const videoAPI = {
  createJob: async (images: File[], aspectRatios: string[], videoProvider?: string) => {
    try {
      const formData = new FormData()
      // FastAPI expects multiple files with the same field name "images"
      images.forEach((image) => {
        formData.append('images', image, image.name)
      })
      formData.append('aspect_ratios', aspectRatios.join(','))
      if (videoProvider) {
        formData.append('video_provider', videoProvider)
      }
      
      const token = localStorage.getItem('access_token')
      console.log('Sending request to /api/v1/videos/ with', images.length, 'images')
      console.log('Token present:', !!token, 'Token length:', token?.length || 0)
      console.log('FormData entries:', Array.from(formData.entries()).map(([k, v]) => [k, v instanceof File ? `${v.name} (${v.size} bytes)` : v]))
      
      // FormData - axios will automatically set Content-Type: multipart/form-data with boundary
      const response = await api.post('/api/v1/videos/', formData, {
        maxContentLength: Infinity,
        maxBodyLength: Infinity
      })
      console.log('Response received:', response.status, response.data)
      return response.data
    } catch (error: any) {
      console.error('API error in createJob:', error)
      console.error('Error response:', error.response?.data)
      console.error('Error status:', error.response?.status)
      console.error('Error message:', error.message)
      
      // Check error type and provide appropriate message
      if (error.response) {
        // Server responded, so it's NOT a network error
        if (error.response.status === 401) {
          console.error('Authentication failed - token may be expired or invalid')
          localStorage.removeItem('access_token')
          // Let the original error propagate so VideoUpload can handle it properly
          throw error
        }
        // Extract error message from FastAPI response
        const detail = error.response?.data?.detail
        let errorMessage = error.message || 'Request failed'
        
        if (Array.isArray(detail)) {
          // FastAPI validation errors are arrays of objects
          errorMessage = detail.map((err: any) => {
            const loc = Array.isArray(err.loc) ? err.loc.slice(1).join('.') : ''
            return `${loc ? loc + ': ' : ''}${err.msg || JSON.stringify(err)}`
          }).join(', ')
        } else if (typeof detail === 'string') {
          errorMessage = detail
        } else if (detail && typeof detail === 'object') {
          errorMessage = JSON.stringify(detail)
        }
        
        const serverError = new Error(errorMessage)
        // Preserve response for component error handling
        ;(serverError as any).response = error.response
        throw serverError
      } else {
        // No response from server - could be network error, CORS, timeout, or other connection issue
        // Log the actual error for debugging
        console.error('No response from server. Error details:', {
          code: error.code,
          message: error.message,
          name: error.name,
          stack: error.stack
        })
        
        // Check for specific error types
        if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error') || error.message?.includes('Failed to fetch')) {
          // Check if backend is actually reachable
          const backendCheck = await fetch('http://localhost:8000/health').catch(() => null)
          if (!backendCheck || !backendCheck.ok) {
            const networkError = new Error('Network error: Cannot connect to backend. Please ensure the backend server is running on http://localhost:8000')
            throw networkError
          }
          // Backend is reachable but this request failed - might be CORS or other issue
          throw new Error(`Request failed: ${error.message || 'Network error. Backend is running but request could not be completed.'}`)
        }
        
        if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
          const networkError = new Error('Network error: Cannot connect to backend. Please ensure the backend server is running on http://localhost:8000')
          throw networkError
        }
        
        // Unknown error without response - include original message with more context
        throw new Error(error.message || `Request failed: ${String(error)}. Check browser console for details.`)
      }
    }
  },
  
  getJob: async (jobId: string) => {
    const response = await api.get(`/api/v1/videos/${jobId}`)
    return response.data
  },
  
  listJobs: async () => {
    const response = await api.get('/api/v1/videos/')
    return response.data
  },
  
  deleteJob: async (jobId: string) => {
    const response = await api.delete(`/api/v1/videos/${jobId}`)
    return response.data
  },
}

export default api


