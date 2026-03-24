import { StrictMode, lazy, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { ErrorBoundary } from './components/ErrorBoundary'
import { initToast } from './components/Toast'
import LoadingFallback from './components/LoadingFallback'
import GlobalErrorFallback from './components/GlobalErrorFallback'

// 初始化全局 Toast 通知
initToast()

// 懒加载 App 组件以减少初始包大小
const App = lazy(() => import('./App'))

// 主渲染函数
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