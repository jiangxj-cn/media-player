import { useState, useEffect } from 'react'
import SearchBar from './components/SearchBar'
import Player from './components/Player'
import MiniPlayer from './components/MiniPlayer'
import SearchResults from './components/SearchResults'
import PlaylistPanel from './components/PlaylistPanel'
import FavoritesPanel from './components/FavoritesPanel'
import HistoryPanel from './components/HistoryPanel'
import { AuthModal } from './components/Auth'
import UserAvatar from './components/UserAvatar'
import ThemeToggle from './components/ThemeToggle'
import { usePlayerStore } from './stores/playerStore'
import { useAuthStore } from './stores/authStore'
import type { MediaItem } from './types'

function App() {
  const { currentMedia, setCurrentMedia, loadFromDB, syncWithServer } = usePlayerStore()
  const { isAuthenticated, checkAuth } = useAuthStore()
  const [searchResults, setSearchResults] = useState<MediaItem[]>([])
  const [activeTab, setActiveTab] = useState<'playlist' | 'favorites' | 'history'>('playlist')
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authModalView, setAuthModalView] = useState<'login' | 'register'>('login')
  const [showSidebar, setShowSidebar] = useState(true)
  const [customUrl, setCustomUrl] = useState('')
  const [showUrlInput, setShowUrlInput] = useState(false)
  
  // Initialize auth state and load data from DB
  useEffect(() => {
    const init = async () => {
      await checkAuth()
      await loadFromDB()
    }
    init()
  }, [checkAuth, loadFromDB])
  
  // Sync data when user logs in
  useEffect(() => {
    if (isAuthenticated) {
      syncWithServer()
    }
  }, [isAuthenticated, syncWithServer])
  
  // Listen for logout events
  useEffect(() => {
    const handleLogout = () => {
      // Clear local state on logout
      setCurrentMedia(null)
    }
    
    window.addEventListener('auth:logout', handleLogout)
    return () => window.removeEventListener('auth:logout', handleLogout)
  }, [setCurrentMedia])

  // 响应式侧边栏控制
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setShowSidebar(false)
      } else {
        setShowSidebar(true)
      }
    }
    
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([])
      return
    }
    
    try {
      // 调用后端搜索 API
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&source=all&max_results=10`)
      const data = await response.json()
      
      // 转换搜索结果格式
      const results: MediaItem[] = (data.results || []).map((item: any, index: number) => ({
        id: item.id || `${item.source}-${index}`,
        url: item.url,
        title: item.title,
        thumbnail: item.thumbnail,
        duration: typeof item.duration === 'string' ? parseDuration(item.duration) : item.duration,
        source: item.source || 'other'
      }))
      
      setSearchResults(results)
    } catch (error) {
      console.error('Search failed:', error)
      // 显示错误提示
      setSearchResults([])
    }
  }
  
  // 解析时长字符串 (如 "3:45" -> 225 秒)
  const parseDuration = (duration: string): number => {
    if (!duration) return 0
    const parts = duration.split(':').map(Number)
    if (parts.length === 2) {
      return parts[0] * 60 + parts[1]
    } else if (parts.length === 3) {
      return parts[0] * 3600 + parts[1] * 60 + parts[2]
    }
    return parseInt(duration) || 0
  }

  const handlePlay = async (item: MediaItem) => {
    // YouTube/B站视频需要先提取流 URL
    if (item.source === 'youtube' || item.source === 'bilibili') {
      try {
        const response = await fetch(`/api/extract?url=${encodeURIComponent(item.url)}&format=best`)
        const data = await response.json()
        
        if (data.direct_url) {
          // 使用后端代理播放（避免 403）
          const proxyUrl = `/api/proxy?url=${encodeURIComponent(data.direct_url)}`
          const playItem = {
            ...item,
            url: proxyUrl,
            title: data.title || item.title,
            thumbnail: data.thumbnail || item.thumbnail,
            duration: data.duration || item.duration
          }
          setCurrentMedia(playItem)
          
          // 记录到历史
          fetch('/api/history', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              media_url: item.url,
              title: playItem.title,
              thumbnail: playItem.thumbnail,
              position: 0,
              duration: playItem.duration
            })
          }).catch(e => console.error('History error:', e))
        } else {
          console.error('No direct URL found')
        }
      } catch (e) {
        console.error('Failed to extract media:', e)
      }
    } else {
      // 其他来源直接播放
      setCurrentMedia(item)
    }
  }

  const [customUrl, setCustomUrl] = useState('')
  const [showUrlInput, setShowUrlInput] = useState(false)

  const handleCustomUrlPlay = () => {
    if (!customUrl.trim()) return
    
    // 创建自定义媒体项
    const customMedia: MediaItem = {
      id: `custom-${Date.now()}`,
      url: customUrl.trim(),
      title: '自定义视频',
      thumbnail: '',
      duration: 0,
      source: 'custom'
    }
    
    // 直接播放（m3u8 或 mp4）
    setCurrentMedia(customMedia)
    setCustomUrl('')
    setShowUrlInput(false)
    
    // 记录历史
    fetch('/api/history', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        media_url: customUrl.trim(),
        title: '自定义视频',
        thumbnail: '',
        position: 0,
        duration: 0
      })
    }).catch(e => console.error('History error:', e))
  }
    setAuthModalView('login')
    setShowAuthModal(true)
  }

  const handleAuthSuccess = () => {
    setShowAuthModal(false)
    syncWithServer()
  }

  const renderSidebarContent = () => {
    switch (activeTab) {
      case 'playlist':
        return <PlaylistPanel />
      case 'favorites':
        return <FavoritesPanel onPlay={handlePlay} />
      case 'history':
        return <HistoryPanel onPlay={handlePlay} />
    }
  }

  return (
    <div className="flex h-screen bg-bg-primary text-white">
      {/* Mobile Sidebar Toggle */}
      <button
        onClick={() => setShowSidebar(!showSidebar)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-gray-800 rounded-lg shadow-lg"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Sidebar - 响应式布局 */}
      <aside className={`
        fixed md:relative
        z-40
        w-80 md:w-80
        h-full
        bg-gray-900 md:bg-gray-900
        border-r border-gray-800
        transform transition-transform duration-300 ease-in-out
        ${showSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        flex flex-col
      `}>
        {/* User Header */}
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                <span className="text-primary">🎵</span>
              </div>
              <div>
                <h3 className="font-medium">Media Player</h3>
                <p className="text-xs text-gray-400">
                  {isAuthenticated ? '已登录' : '访客模式'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <UserAvatar onLoginClick={handleLoginClick} />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-800">
          <button
            onClick={() => setActiveTab('playlist')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'playlist'
                ? 'text-primary border-b-2 border-primary'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            播放列表
          </button>
          <button
            onClick={() => setActiveTab('favorites')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'favorites'
                ? 'text-primary border-b-2 border-primary'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            收藏
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'history'
                ? 'text-primary border-b-2 border-primary'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            历史
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {renderSidebarContent()}
        </div>
      </aside>

      {/* Sidebar Overlay for Mobile */}
      {showSidebar && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-30"
          onClick={() => setShowSidebar(false)}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="p-6 pb-4 pt-16 md:pt-6">
          <div className="flex gap-2">
            <div className="flex-1">
              <SearchBar onSearch={handleSearch} />
            </div>
            {/* 自定义 URL 按钮 */}
            <button
              onClick={() => setShowUrlInput(!showUrlInput)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm flex items-center gap-2"
              title="直接播放视频链接"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              链接
            </button>
          </div>
          
          {/* URL 输入框 */}
          {showUrlInput && (
            <div className="mt-3 flex gap-2">
              <input
                type="text"
                value={customUrl}
                onChange={(e) => setCustomUrl(e.target.value)}
                placeholder="输入视频链接 (支持 m3u8/mp4)"
                className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                onKeyDown={(e) => e.key === 'Enter' && handleCustomUrlPlay()}
              />
              <button
                onClick={handleCustomUrlPlay}
                className="px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg font-medium"
              >
                播放
              </button>
            </div>
          )}
        </div>

        {/* Player Section */}
        <div className="px-6 pb-4">
          <Player media={currentMedia} />
        </div>

        {/* Search Results - 响应式布局 */}
        {searchResults.length > 0 && (
          <div className="flex-1 overflow-auto px-6 pb-24">
            <h3 className="text-lg font-bold mb-4">搜索结果</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              <SearchResults results={searchResults} onPlay={handlePlay} />
            </div>
          </div>
        )}

        {/* Mini Player */}
        <MiniPlayer />
      </main>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        defaultView={authModalView}
        onAuthSuccess={handleAuthSuccess}
      />
    </div>
  )
}

export default App
