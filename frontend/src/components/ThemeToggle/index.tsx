import { useState, useEffect, useCallback } from 'react'

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(true)

  const applyTheme = useCallback((dark: boolean) => {
    if (dark) {
      document.documentElement.classList.remove('light')
      document.documentElement.setAttribute('data-theme', 'dark')
    } else {
      document.documentElement.classList.add('light')
      document.documentElement.setAttribute('data-theme', 'light')
    }
  }, [])

  useEffect(() => {
    // 从 localStorage 加载主题偏好
    const saved = localStorage.getItem('theme')
    if (saved) {
      const dark = saved === 'dark'
      // 使用 queueMicrotask 避免同步 setState 警告
      queueMicrotask(() => {
        setIsDark(dark)
        applyTheme(dark)
      })
    }
  }, [applyTheme])

  const toggleTheme = () => {
    const newDark = !isDark
    setIsDark(newDark)
    applyTheme(newDark)
    localStorage.setItem('theme', newDark ? 'dark' : 'light')
  }

  return (
    <button
      onClick={toggleTheme}
      className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
      title={isDark ? '切换到浅色模式' : '切换到深色模式'}
    >
      {isDark ? (
        <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 3a1 1 0 011 1v1a1 1 0 11-2 0V4a1 1 0 011-1zm0 15a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm9-8a1 1 0 110 2h-1a1 1 0 110-2h1zM5 11a1 1 0 110 2H4a1 1 0 110-2h1zm14.071-5.071a1 1 0 010 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM7.05 16.95a1 1 0 010 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zm11.9 0a1 1 0 011.414 0l.707.707a1 1 0 11-1.414 1.414l-.707-.707a1 1 0 010-1.414zM7.05 7.05a1 1 0 011.414 0l.707.707A1 1 0 117.757 9.17l-.707-.707a1 1 0 010-1.414zM12 8a4 4 0 100 8 4 4 0 000-8z" />
        </svg>
      ) : (
        <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      )}
    </button>
  )
}
