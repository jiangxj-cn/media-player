import { usePlayerStore } from '../../stores/playerStore'
import type { HistoryItem, MediaItem } from '../../types'

interface HistoryPanelProps {
  onPlay?: (item: MediaItem) => void
}

export default function HistoryPanel({ onPlay }: HistoryPanelProps) {
  const { history, clearHistory } = usePlayerStore()

  const handlePlay = (item: HistoryItem) => {
    // 让父组件的 handlePlay 处理 API 调用（获取嵌入播放器等）
    const mediaItem: MediaItem = {
      id: item.id,
      url: item.url,
      title: item.title,
      thumbnail: item.thumbnail,
      duration: item.duration,
      source: item.source
    }
    onPlay?.(mediaItem)
  }

  const formatTimeAgo = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - new Date(date).getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    return `${days}天前`
  }

  if (history.length === 0) {
    return (
      <div className="text-center text-gray-400 py-8">
        <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p>暂无播放历史</p>
        <p className="text-sm mt-2">播放的歌曲将显示在这里</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {history.map((item) => (
        <div
          key={`${item.id}-${item.playedAt}`}
          className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-700/50 transition-colors group"
        >
          <div
            className="flex-1 min-w-0 cursor-pointer"
            onClick={() => handlePlay(item)}
          >
            <div className="flex items-center gap-2">
              <h4 className="font-medium text-white truncate">{item.title}</h4>
              {item.position > 0 && (
                <span className="text-xs text-primary">
                  {Math.floor(item.position / 60)}:{String(item.position % 60).padStart(2, '0')}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span>{item.source}</span>
              <span>•</span>
              <span>{formatTimeAgo(item.playedAt)}</span>
            </div>
          </div>
          
          <button
            onClick={() => handlePlay(item)}
            className="opacity-0 group-hover:opacity-100 p-2 hover:bg-primary/20 hover:text-primary rounded transition-all"
            title="继续播放"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </button>
        </div>
      ))}

      {history.length > 0 && (
        <div className="pt-4 mt-4 border-t border-gray-700">
          <button
            onClick={clearHistory}
            className="w-full py-2 text-sm text-gray-400 hover:text-red-400 transition-colors"
          >
            清空历史记录
          </button>
        </div>
      )}
    </div>
  )
}
