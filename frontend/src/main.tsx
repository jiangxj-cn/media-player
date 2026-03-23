import { StrictMode, lazy, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { ErrorBoundary } from './components/ErrorBoundary'
import { initToast } from './components/Toast'

// 初始化全局 Toast 通知
initToast()

// 懒加载 App 组件以减少初始包大小
const App = lazy(() => import('./App'))

// 加载中组件
function LoadingFallback() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin text-4xl mb-4">🎵</div>
        <p className="text-gray-400">加载中...</p>
      </div>
    </div>
  )
}

// 全局错误回退
function GlobalErrorFallback() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="text-center">
        <div className="text-6xl mb-4">😢</div>
        <h1 className="text-2xl font-bold text-white mb-2">出错了</h1>
        <p className="text-gray-400 mb-4">应用加载失败，请刷新页面重试</p>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2 bg-primary hover:bg-primary/80 text-white rounded-lg transition-colors"
        >
          刷新页面
        </button>
      </div>
    </div>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary fallback={<GlobalErrorFallback />}>
      <Suspense fallback={<LoadingFallback />}>
        <App />
      </Suspense>
    </ErrorBoundary>
  </StrictMode>,
)

// Register Service Worker for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('ServiceWorker registration successful:', registration.scope)
      })
      .catch((err) => {
        console.log('ServiceWorker registration failed:', err)
      })
  })
}