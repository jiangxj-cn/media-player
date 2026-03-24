import { useEffect, useState, useCallback } from 'react'
import { setAddToast } from './toast'
import type { ToastType } from './toast'

interface ToastConfig {
  message: string
  type: ToastType
  duration?: number
}

interface ToastItem extends ToastConfig {
  id: number
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  useEffect(() => {
    setAddToast((config: ToastConfig) => {
      const id = Date.now() + Math.random()
      setToasts(prev => [...prev, { ...config, id }])
      
      const duration = config.duration || 3000
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id))
      }, duration)
    })
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

function ToastMessage({ toast, onClose }: { toast: ToastItem; onClose: () => void }) {
  const icons: Record<ToastType, string> = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  }

  const colors: Record<ToastType, string> = {
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