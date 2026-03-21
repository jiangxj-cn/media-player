import { useState } from 'react'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { usePlayerStore } from '../../stores/playerStore'
import type { MediaItem } from '../../types'

function SortableItem({ 
  item, 
  onPlay, 
  onRemove,
  isPlaying 
}: { 
  item: MediaItem
  onPlay: () => void
  onRemove: () => void
  isPlaying: boolean
}) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: item.id })
  
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-3 p-3 rounded-lg transition-all group ${
        isPlaying 
          ? 'bg-primary/20 border border-primary/50' 
          : 'bg-gray-800/50 hover:bg-gray-700/50'
      }`}
    >
      <button
        {...attributes}
        {...listeners}
        className="cursor-grab active:cursor-grabbing p-1 hover:bg-gray-600 rounded"
        title="拖拽排序"
      >
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
        </svg>
      </button>
      
      {/* Playing Indicator */}
      {isPlaying && (
        <div className="flex items-end gap-0.5 w-4 h-4">
          <div className="w-1 bg-primary rounded-full animate-pulse" style={{ height: '60%', animationDelay: '0ms' }} />
          <div className="w-1 bg-primary rounded-full animate-pulse" style={{ height: '100%', animationDelay: '150ms' }} />
          <div className="w-1 bg-primary rounded-full animate-pulse" style={{ height: '40%', animationDelay: '300ms' }} />
        </div>
      )}
      
      <div
        className="flex-1 min-w-0 cursor-pointer"
        onDoubleClick={onPlay}
        onClick={onPlay}
      >
        <h4 className={`font-medium truncate ${isPlaying ? 'text-primary' : 'text-white'}`}>
          {item.title}
        </h4>
        <p className="text-xs text-gray-400">{item.source}</p>
      </div>
      
      <button
        onClick={(e) => {
          e.stopPropagation()
          onRemove()
        }}
        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 hover:text-red-400 rounded transition-all"
        title="移除"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}

export default function PlaylistPanel() {
  const { 
    playlist, 
    currentMedia,
    setCurrentMedia, 
    removeFromPlaylist, 
    clearPlaylist,
    setPlaylist
  } = usePlayerStore()
  
  const [activeTab] = useState<'playlist' | 'favorites' | 'history'>('playlist')
  const { favorites, history } = usePlayerStore()

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 防止误触，需要拖动 8px 才激活
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    
    if (!over || active.id === over.id) return

    const oldIndex = playlist.findIndex(item => item.id === active.id)
    const newIndex = playlist.findIndex(item => item.id === over.id)
    
    if (oldIndex === -1 || newIndex === -1) return

    // 创建新的播放列表顺序
    const newPlaylist = [...playlist]
    const [removed] = newPlaylist.splice(oldIndex, 1)
    newPlaylist.splice(newIndex, 0, removed)
    
    setPlaylist(newPlaylist)
  }

  const handlePlay = (item: MediaItem) => {
    setCurrentMedia(item)
  }

  const renderPlaylist = () => {
    if (playlist.length === 0) {
      return (
        <div className="text-center text-gray-400 py-8">
          <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
          </svg>
          <p>暂无播放列表</p>
          <p className="text-sm mt-2">搜索歌曲并添加到播放列表</p>
        </div>
      )
    }

    return (
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={playlist.map(i => i.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-2">
            {playlist.map((item) => (
              <SortableItem
                key={item.id}
                item={item}
                onPlay={() => handlePlay(item)}
                onRemove={() => removeFromPlaylist(item.id)}
                isPlaying={currentMedia?.id === item.id}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    )
  }

  const renderFavorites = () => {
    if (favorites.length === 0) {
      return (
        <div className="text-center text-gray-400 py-8">
          <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <p>暂无收藏</p>
        </div>
      )
    }

    return (
      <div className="space-y-2">
        {favorites.map((item) => (
          <SortableItem
            key={item.id}
            item={item}
            onPlay={() => handlePlay(item)}
            onRemove={() => removeFromPlaylist(item.id)}
            isPlaying={currentMedia?.id === item.id}
          />
        ))}
      </div>
    )
  }

  const renderHistory = () => {
    if (history.length === 0) {
      return (
        <div className="text-center text-gray-400 py-8">
          <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>暂无播放历史</p>
        </div>
      )
    }

    return (
      <div className="space-y-2">
        {history.map((item) => (
          <div
            key={item.id}
            onClick={() => handlePlay(item)}
            className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-700/50 transition-colors cursor-pointer group"
          >
            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-white truncate">{item.title}</h4>
              <p className="text-xs text-gray-400">
                {new Date(item.playedAt).toLocaleDateString()} · 看到 {Math.floor(item.position / 60)}:{String(Math.floor(item.position % 60)).padStart(2, '0')}
              </p>
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'playlist':
        return renderPlaylist()
      case 'favorites':
        return renderFavorites()
      case 'history':
        return renderHistory()
      default:
        return null
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Content */}
      <div className="flex-1 overflow-auto -mx-2 px-2">
        {renderContent()}
      </div>

      {/* Actions */}
      {playlist.length > 0 && activeTab === 'playlist' && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <button
            onClick={clearPlaylist}
            className="w-full py-2 text-sm text-gray-400 hover:text-red-400 transition-colors"
          >
            清空播放列表
          </button>
        </div>
      )}
    </div>
  )
}
