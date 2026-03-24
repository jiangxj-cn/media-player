import { useState } from 'react'
import { usePlayerStore } from '../../stores/playerStore'
import type { MediaItem } from '../../types'
import { api } from '../../utils/api'

interface SearchResultsProps {
  results: MediaItem[]
  onPlay?: (item: MediaItem) => void
}

export default function SearchResults({ results, onPlay }: SearchResultsProps) {
  const { addToPlaylist, addToFavorites, favorites, removeFromFavorites } = usePlayerStore()
  const [downloadingId, setDownloadingId] = useState<string | null>(null)
  const [downloadProgress, setDownloadProgress] = useState<Record<string, number>>({})

  const handlePlay = (item: MediaItem) => {
    // 不要直接设置 currentMedia，让父组件的 handlePlay 处理 API 调用
    onPlay?.(item)
  }

  const handleAddToPlaylist = (e: React.MouseEvent, item: MediaItem) => {
    e.stopPropagation()
    addToPlaylist(item)
  }

  const handleToggleFavorite = (e: React.MouseEvent, item: MediaItem) => {
    e.stopPropagation()
    const isFavorite = favorites.some(f => f.id === item.id)
    if (isFavorite) {
      removeFromFavorites(item.id)
    } else {
      addToFavorites(item)
    }
  }

  const handleDownload = async (e: React.MouseEvent, item: MediaItem) => {
    e.stopPropagation()
    
    if (downloadingId === item.id) return
    
    setDownloadingId(item.id)
    setDownloadProgress(prev => ({ ...prev, [item.id]: 0 }))
    
    try {
      // 调用后端下载 API
      const response = await api.post<{ 
        success: boolean
        downloadId?: string
        error?: string
      }>('/api/download', {
        mediaId: item.id,
        url: item.url,
        title: item.title
      })
      
      if (response.success && response.downloadId) {
        // 模拟下载进度（实际应该通过 WebSocket 或轮询获取真实进度）
        const interval = setInterval(() => {
          setDownloadProgress(prev => {
            const current = prev[item.id] || 0
            if (current >= 100) {
              clearInterval(interval)
              setDownloadingId(null)
              return prev
            }
            return { ...prev, [item.id]: current + 10 }
          })
        }, 200)
        
        // 2 秒后完成下载
        setTimeout(() => {
          setDownloadProgress(prev => ({ ...prev, [item.id]: 100 }))
          setDownloadingId(null)
          
          // 显示下载完成通知
          window.dispatchEvent(new CustomEvent('download:complete', {
            detail: { mediaId: item.id, title: item.title }
          }))
        }, 2000)
      } else {
        console.error('Download failed:', response.error)
        setDownloadingId(null)
      }
    } catch (error) {
      console.error('Download error:', error)
      setDownloadingId(null)
    }
  }

  const isFavorite = (id: string) => favorites.some(f => f.id === id)

  if (results.length === 0) {
    return null
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {results.map((item) => {
        const isDownloading = downloadingId === item.id
        const progress = downloadProgress[item.id] || 0
        
        return (
          <div
            key={item.id}
            onClick={() => handlePlay(item)}
            className="group bg-gray-800/50 rounded-lg overflow-hidden hover:bg-gray-700/50 transition-all cursor-pointer"
          >
            {/* Thumbnail */}
            <div className="relative aspect-video bg-gray-900">
              {item.thumbnail ? (
                <img
                  src={item.thumbnail}
                  alt={item.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <svg className="w-12 h-12 text-gray-700" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
                  </svg>
                </div>
              )}
              
              {/* Play Button Overlay */}
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <button className="p-3 bg-primary rounded-full hover:bg-primary/90 transition-colors">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </button>
              </div>

              {/* Duration Badge */}
              {item.duration && (
                <span className="absolute bottom-2 right-2 px-2 py-1 bg-black/80 text-white text-xs rounded">
                  {Math.floor(item.duration / 60)}:{String(item.duration % 60).padStart(2, '0')}
                </span>
              )}
              
              {/* Download Progress Overlay */}
              {isDownloading && (
                <div className="absolute inset-0 bg-black/70 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                    <p className="text-white text-sm">{progress}%</p>
                  </div>
                </div>
              )}
            </div>

            {/* Info */}
            <div className="p-3">
              <h4 className="font-medium text-white text-sm truncate mb-1">{item.title}</h4>
              <p className="text-xs text-gray-400 mb-3">{item.source}</p>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <button
                  onClick={(e) => handleAddToPlaylist(e, item)}
                  className="flex-1 py-1.5 px-3 bg-gray-700 hover:bg-gray-600 rounded text-xs transition-colors flex items-center justify-center gap-1"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  添加
                </button>
                
                <button
                  onClick={(e) => handleDownload(e, item)}
                  disabled={isDownloading}
                  className={`p-1.5 rounded transition-colors ${
                    isDownloading
                      ? 'text-primary bg-primary/10'
                      : 'text-gray-400 hover:text-primary hover:bg-gray-700'
                  }`}
                  title={isDownloading ? '下载中...' : '下载'}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </button>
                
                <button
                  onClick={(e) => handleToggleFavorite(e, item)}
                  className={`p-1.5 rounded transition-colors ${
                    isFavorite(item.id)
                      ? 'text-red-400 bg-red-400/10'
                      : 'text-gray-400 hover:text-red-400 hover:bg-gray-700'
                  }`}
                >
                  <svg className="w-4 h-4" fill={isFavorite(item.id) ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
