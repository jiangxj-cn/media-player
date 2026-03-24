import { usePlayerStore } from '../../stores/playerStore'
import type { MediaItem } from '../../types'

interface FavoritesPanelProps {
  onPlay?: (item: MediaItem) => void
}

export default function FavoritesPanel({ onPlay }: FavoritesPanelProps) {
  const { favorites, removeFromFavorites } = usePlayerStore()

  const handlePlay = (item: MediaItem) => {
    // 让父组件的 handlePlay 处理 API 调用（获取嵌入播放器等）
    onPlay?.(item)
  }

  if (favorites.length === 0) {
    return (
      <div className="text-center text-gray-400 py-8">
        <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
        <p>暂无收藏</p>
        <p className="text-sm mt-2">点击收藏按钮添加喜欢的歌曲</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {favorites.map((item) => (
        <div
          key={item.id}
          className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-700/50 transition-colors group"
        >
          <div
            className="flex-1 min-w-0 cursor-pointer"
            onClick={() => handlePlay(item)}
            onDoubleClick={() => handlePlay(item)}
          >
            <h4 className="font-medium text-white truncate">{item.title}</h4>
            <p className="text-xs text-gray-400">{item.source}</p>
          </div>
          
          <button
            onClick={() => removeFromFavorites(item.id)}
            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 hover:text-red-400 rounded transition-all"
            title="取消收藏"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  )
}
