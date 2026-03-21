import { useState, useRef, useEffect } from 'react'
import { useAuthStore } from '../../stores/authStore'

interface UserAvatarProps {
  onLoginClick: () => void
}

export default function UserAvatar({ onLoginClick }: UserAvatarProps) {
  const { user, isAuthenticated, logout } = useAuthStore()
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }
    
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])
  
  if (!isAuthenticated || !user) {
    return (
      <button
        onClick={onLoginClick}
        className="px-4 py-2 bg-primary hover:bg-primary/90 text-white text-sm font-medium rounded-lg transition-colors"
      >
        登录
      </button>
    )
  }
  
  const initials = user.username.charAt(0).toUpperCase()
  
  const handleLogout = () => {
    setShowDropdown(false)
    logout()
  }
  
  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="w-10 h-10 bg-gradient-to-br from-primary to-purple-600 rounded-full flex items-center justify-center text-white font-bold hover:ring-2 hover:ring-primary/50 transition-all"
      >
        {initials}
      </button>
      
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg py-1 z-50">
          <div className="px-4 py-3 border-b border-gray-700">
            <p className="text-sm font-medium text-white truncate">{user.username}</p>
            <p className="text-xs text-gray-400 mt-0.5">已登录</p>
          </div>
          
          <button
            onClick={() => setShowDropdown(false)}
            className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            个人中心
          </button>
          
          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-gray-700 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            退出登录
          </button>
        </div>
      )}
    </div>
  )
}