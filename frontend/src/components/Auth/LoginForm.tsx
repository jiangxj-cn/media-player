import { useState } from 'react'
import { useAuthStore } from '../../stores/authStore'

interface LoginFormProps {
  onLogin: (token: string) => void
  onSwitchToRegister: () => void
  onClose: () => void
}

export default function LoginForm({ onLogin, onSwitchToRegister, onClose }: LoginFormProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)
  
  const { login, isLoading, error, clearError } = useAuthStore()
  
  const validateForm = (): boolean => {
    if (!username.trim()) {
      setValidationError('请输入用户名')
      return false
    }
    if (username.length < 3) {
      setValidationError('用户名至少需要3个字符')
      return false
    }
    if (!password) {
      setValidationError('请输入密码')
      return false
    }
    if (password.length < 6) {
      setValidationError('密码至少需要6个字符')
      return false
    }
    return true
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setValidationError(null)
    clearError()
    
    if (!validateForm()) return
    
    try {
      await login(username.trim(), password)
      const token = localStorage.getItem('auth_token')
      if (token) {
        onLogin(token)
        onClose()
      }
    } catch {
      // Error is handled by the store
    }
  }
  
  const displayError = validationError || error
  
  return (
    <div className="w-full max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-white mb-6 text-center">登录</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="login-username" className="block text-sm font-medium text-gray-300 mb-1">
            用户名
          </label>
          <input
            id="login-username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            placeholder="请输入用户名"
            disabled={isLoading}
            autoComplete="username"
          />
        </div>
        
        <div>
          <label htmlFor="login-password" className="block text-sm font-medium text-gray-300 mb-1">
            密码
          </label>
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            placeholder="请输入密码"
            disabled={isLoading}
            autoComplete="current-password"
          />
        </div>
        
        {displayError && (
          <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm">
            {displayError}
          </div>
        )}
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2 bg-primary hover:bg-primary/90 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? '登录中...' : '登录'}
        </button>
      </form>
      
      <div className="mt-6 text-center text-gray-400 text-sm">
        还没有账号？{' '}
        <button
          type="button"
          onClick={onSwitchToRegister}
          className="text-primary hover:text-primary/80 transition-colors"
        >
          立即注册
        </button>
      </div>
    </div>
  )
}