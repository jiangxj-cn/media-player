import { createRoot } from 'react-dom/client'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

interface ToastConfig {
  message: string
  type: ToastType
  duration?: number
}

let addToast: (config: ToastConfig) => void

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

// 内部函数：设置 addToast 回调
export const setAddToast = (fn: (config: ToastConfig) => void) => {
  addToast = fn
}

// 初始化 Toast 容器
let initialized = false
export const initToast = () => {
  if (initialized) return
  initialized = true
  
  // 动态导入组件避免循环依赖
  import('./ToastContainer').then(({ default: ToastContainer }) => {
    const container = document.createElement('div')
    container.id = 'toast-container'
    document.body.appendChild(container)
    createRoot(container).render(<ToastContainer />)
  })
}