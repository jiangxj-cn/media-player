const API_BASE = import.meta.env.VITE_API_BASE || ''

export interface ApiError {
  status: number
  message: string
  name: 'ApiError'
}

function createApiError(status: number, message: string): ApiError {
  return { status, message, name: 'ApiError' }
}

function isApiError(error: unknown): error is ApiError {
  return typeof error === 'object' && error !== null && (error as ApiError).name === 'ApiError'
}

interface RequestOptions extends RequestInit {
  skipAuth?: boolean
}

function getAuthToken(): string | null {
  return localStorage.getItem('auth_token')
}

function setAuthToken(token: string | null): void {
  if (token) {
    localStorage.setItem('auth_token', token)
  } else {
    localStorage.removeItem('auth_token')
  }
}

function clearAuth(): void {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('auth_user')
  // Trigger custom event for auth state change
  window.dispatchEvent(new CustomEvent('auth:logout'))
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { skipAuth = false, ...fetchOptions } = options
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  const token = getAuthToken()
  if (token && !skipAuth) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`
  }
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...fetchOptions,
    headers,
  })
  
  if (response.status === 401) {
    clearAuth()
    throw createApiError(401, 'Unauthorized')
  }
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw createApiError(response.status, errorData.error || response.statusText)
  }
  
  // Handle empty responses
  const text = await response.text()
  if (!text) {
    return {} as T
  }
  
  return JSON.parse(text)
}

export const api = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'GET' }),
    
  post: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),
    
  put: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),
    
  delete: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'DELETE' }),
}

export { getAuthToken, setAuthToken, clearAuth, isApiError }
export type { RequestOptions }