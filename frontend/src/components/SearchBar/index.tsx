/**
 * 搜索栏组件 - 带防抖优化
 */

import { useState, useCallback, useEffect, useRef } from 'react'
import { debounce } from '../../utils/helpers'

interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
  debounceMs?: number
  autoFocus?: boolean
}

export default function SearchBar({ 
  onSearch, 
  placeholder = '搜索音乐、视频...',
  debounceMs = 300,
  autoFocus = false
}: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // 创建防抖搜索函数
  const debouncedSearch = useCallback(
    debounce((value: string) => {
      if (value.trim()) {
        onSearch(value.trim())
      }
    }, debounceMs),
    [onSearch, debounceMs]
  )

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    debouncedSearch(value)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }

  const handleClear = () => {
    setQuery('')
    inputRef.current?.focus()
  }

  // 键盘快捷键: Ctrl/Cmd + K 聚焦搜索框
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className={`
        flex items-center gap-2 px-4 py-2.5 bg-gray-800/80 rounded-xl
        transition-all duration-200
        ${isFocused ? 'ring-2 ring-primary/50 bg-gray-800' : ''}
      `}>
        {/* 搜索图标 */}
        <svg 
          className={`w-5 h-5 transition-colors ${isFocused ? 'text-primary' : 'text-gray-400'}`} 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>

        {/* 输入框 */}
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className="flex-1 bg-transparent text-white placeholder-gray-500 focus:outline-none text-sm"
        />

        {/* 清除按钮 */}
        {query && (
          <button
            type="button"
            onClick={handleClear}
            className="p-1 hover:bg-gray-700 rounded-full transition-colors"
          >
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}

        {/* 搜索按钮 */}
        <button
          type="submit"
          className="px-4 py-1.5 bg-primary hover:bg-primary/90 rounded-lg text-sm font-medium transition-colors"
        >
          搜索
        </button>
      </div>

      {/* 快捷键提示 */}
      {!isFocused && !query && (
        <div className="absolute right-12 top-1/2 -translate-y-1/2 hidden md:flex items-center gap-1 text-xs text-gray-500">
          <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-[10px]">⌘</kbd>
          <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-[10px]">K</kbd>
        </div>
      )}
    </form>
  )
}