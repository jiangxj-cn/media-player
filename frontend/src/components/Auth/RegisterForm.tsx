import { useState } from 'react'
import { useAuthStore } from '../../stores/authStore'

interface RegisterFormProps {
  onRegister: () => void
  onSwitchToLogin: () => void
  onClose: () => void
}

export default function RegisterForm({ onRegister, onSwitchToLogin, onClose }: RegisterFormProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)
  
  const { register, isLoading, error, clearError } = useAuthStore()
  
  const validateForm = (): boolean => {
    if (!username.trim()) {
      setValidationError('请输入用户名')
      return false
    }
    if (username.length < 3) {
      setValidationError('用户名至少需要3个字符')
      return false
    }
    if (username.length > 20) {
      setValidationError('用户名不能超过20个字符')
      return false
    }
    if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(username)) {
      setValidationError('用户名只能包含字母、数字、下划线和中文')
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
    if (password.length > 50) {
      setValidationError('密码不能超过50个字符')
      return false
    }
    if (password !== confirmPassword) {
      setValidationError('两次输入的密码不一致')
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
      await register(username.trim(), password)
      onRegister()
      onClose()
    } catch {
      // Error is handled by the store
    }
  }
  
  const displayError = validationError || error
  
  return (
    <div className="w-full max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-white mb-6 text-center">注册</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="register-username" className="block text-sm font-medium text-gray-300 mb-1">
            用户名
          </label>
          <input
            id="register-username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            placeholder="3-20个字符，字母数字下划线中文"
            disabled={isLoading}
            autoComplete="username"
          />
        </div>
        
        <div>
          <label htmlFor="register-password" className="block text-sm font-medium text-gray-300 mb-1">
            密码
          </label>
          <input
            id="register-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            placeholder="至少6个字符"
            disabled={isLoading}
            autoComplete="new-password"
          />
        </div>
        
        <div>
          <label htmlFor="register-confirm-password" className="block text-sm font-medium text-gray-300 mb-1">
            确认密码
          </label>
          <input
            id="register-confirm-password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            placeholder="再次输入密码"
            disabled={isLoading}
            autoComplete="new-password"
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
          {isLoading ? '注册中...' : '注册'}
        </button>
      </form>
      
      <div className="mt-6 text-center text-gray-400 text-sm">
        已有账号？{' '}
        <button
          type="button"
          onClick={onSwitchToLogin}
          className="text-primary hover:text-primary/80 transition-colors"
        >
          立即登录
        </button>
      </div>
    </div>
  )
}