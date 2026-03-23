import { useEffect, useState, useCallback } from 'react'
import { createRoot } from 'react-dom/client'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

interface ToastConfig {
  message: string
  type: ToastType
  duration?: number
}

interface ToastItem extends ToastConfig {
  id: number
}

let toastId = 0
let addToast: (config: ToastConfig) => void

const ToastContainer = () => {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  useEffect(() => {
    addToast = (config: ToastConfig) => {
      const id = ++toastId
      setToasts(prev => [...prev, { ...config, id }])
      
      const duration = config.duration || 3000
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id))
      }, duration)
    }
  }, [])

  const removeToast = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  if (toasts.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2">
      {toasts.map(toast => (
        <ToastMessage key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  )
}

const ToastMessage = ({ toast, onClose }: { toast: ToastItem; onClose: () => void }) => {
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  }

  const colors = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    warning: 'bg-yellow-600',
    info: 'bg-blue-600'
  }

  return (
    <div 
      className={`${colors[toast.type]} text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 min-w-[280px] animate-slide-in`}
      onClick={onClose}
    >
      <span className="text-lg">{icons[toast.type]}</span>
      <span className="flex-1 text-sm">{toast.message}</span>
      <button 
        className="text-white/70 hover:text-white transition-colors"
        onClick={(e) => {
          e.stopPropagation()
          onClose()
        }}
      >
        ✕
      </button>
    </div>
  )
}

// 全局 Toast 函数
export const toast = {
  success: (message: string, duration?: number) => {
    addToast?.({ message, type: 'success', duration })
  },
  error: (message: string, duration?: number) => {
    addToast?.({ message, type: 'error', duration })
  },
  warning: (message: string, duration?: number) => {
    addToast?.({ message, type: 'warning', duration })
  },
  info: (message: string, duration?: number) => {
    addToast?.({ message, type: 'info', duration })
  }
}

// 初始化 Toast 容器
let initialized = false
export const initToast = () => {
  if (initialized) return
  initialized = true
  
  const container = document.createElement('div')
  container.id = 'toast-container'
  document.body.appendChild(container)
  createRoot(container).render(<ToastContainer />)
}

export default ToastContainer