import { useState, useEffect, useRef, type JSX } from 'react'
import { usePlayerStore } from '../../stores/playerStore'
import type { PlayMode } from '../../types'

export default function MiniPlayer() {
  const { 
    currentMedia, 
    isPlaying, 
    togglePlay, 
    playNext, 
    playPrevious,
    playMode,
    setPlayMode,
    setCurrentMedia
  } = usePlayerStore()
  
  const [progress, setProgress] = useState(0)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isDragging, setIsDragging] = useState(false)
  const progressBarRef = useRef<HTMLDivElement>(null)
  
  // 播放模式图标映射
  const playModeIcons: Record<PlayMode, JSX.Element> = {
    'sequence': (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
    'random': (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
    ),
    'loop': (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
    'single-loop': (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        <text x="12" y="18" fontSize="8" textAnchor="middle" fill="currentColor" stroke="none">1</text>
      </svg>
    )
  }
  
  const playModeLabels: Record<PlayMode, string> = {
    'sequence': '顺序播放',
    'random': '随机播放',
    'loop': '列表循环',
    'single-loop': '单曲循环'
  }

  // 切换播放模式
  const togglePlayMode = () => {
    const modes: PlayMode[] = ['sequence', 'random', 'loop', 'single-loop']
    const currentIndex = modes.indexOf(playMode)
    const nextIndex = (currentIndex + 1) % modes.length
    setPlayMode(modes[nextIndex])
  }

  // 模拟进度更新（实际应该从 Player 组件获取）
  useEffect(() => {
    if (!isPlaying || !currentMedia) return

    const interval = setInterval(() => {
      setCurrentTime(prev => {
        const newTime = prev + 1
        if (duration > 0 && newTime >= duration) {
          if (playMode !== 'single-loop') {
            playNext()
          }
          return playMode === 'single-loop' ? 0 : 0
        }
        setProgress((newTime / duration) * 100 || 0)
        return newTime
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [isPlaying, currentMedia, duration, playNext, playMode])

  // 监听来自 Player 组件的时间更新
  useEffect(() => {
    const handleTimeUpdate = (e: Event) => {
      const customEvent = e as CustomEvent<{ currentTime: number; duration: number }>
      setCurrentTime(customEvent.detail.currentTime)
      setDuration(customEvent.detail.duration)
      if (!isDragging) {
        setProgress((customEvent.detail.currentTime / customEvent.detail.duration) * 100 || 0)
      }
    }
    
    window.addEventListener('player:timeupdate', handleTimeUpdate)
    return () => window.removeEventListener('player:timeupdate', handleTimeUpdate)
  }, [isDragging])

  const formatTime = (seconds: number) => {
    if (!seconds || isNaN(seconds)) return '0:00'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${String(secs).padStart(2, '0')}`
  }

  const handleProgressChange = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!duration || !progressBarRef.current) return
    
    const rect = progressBarRef.current.getBoundingClientRect()
    const percent = (e.clientX - rect.left) / rect.width
    const clampedPercent = Math.max(0, Math.min(1, percent))
    const newTime = clampedPercent * duration
    
    setCurrentTime(newTime)
    setProgress(clampedPercent * 100)
    
    // 触发播放器跳转
    window.dispatchEvent(new CustomEvent('player:seek', { 
      detail: { time: newTime } 
    }))
  }

  const handleProgressMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    setIsDragging(true)
    handleProgressChange(e)
  }

  const handleProgressMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDragging) return
    handleProgressChange(e)
  }

  const handleProgressMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleProgressMouseMove as any)
      window.addEventListener('mouseup', handleProgressMouseUp)
      return () => {
        window.removeEventListener('mousemove', handleProgressMouseMove as any)
        window.removeEventListener('mouseup', handleProgressMouseUp)
      }
    }
  }, [isDragging])

  if (!currentMedia) {
    return null
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur-lg border-t border-gray-800 px-4 py-3 z-50">
      {/* Progress Bar */}
      <div
        ref={progressBarRef}
        className="absolute top-0 left-0 right-0 h-1 bg-gray-700 cursor-pointer group"
        onMouseDown={handleProgressMouseDown}
      >
        <div
          className="h-full bg-primary relative transition-all"
          style={{ width: `${progress}%` }}
        >
          <div className={`absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-primary rounded-full transition-opacity ${
            isDragging || 'group-hover:opacity-100 opacity-0'
          }`} />
        </div>
      </div>

      <div className="flex items-center gap-4 max-w-screen-2xl mx-auto">
        {/* Thumbnail */}
        {currentMedia.thumbnail ? (
          <img
            src={currentMedia.thumbnail}
            alt={currentMedia.title}
            className="w-12 h-12 object-cover rounded"
          />
        ) : (
          <div className="w-12 h-12 bg-gray-800 rounded flex items-center justify-center">
            <svg className="w-6 h-6 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
            </svg>
          </div>
        )}

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-white truncate text-sm">{currentMedia.title}</h4>
          <p className="text-xs text-gray-400">{currentMedia.source}</p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          {/* Play Mode Toggle */}
          <button
            onClick={togglePlayMode}
            className="p-2 hover:bg-gray-800 rounded-full transition-colors"
            title={playModeLabels[playMode]}
          >
            {playModeIcons[playMode]}
          </button>
          
          <button
            onClick={playPrevious}
            className="p-2 hover:bg-gray-800 rounded-full transition-colors"
            title="上一首"
          >
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z" />
            </svg>
          </button>

          <button
            onClick={togglePlay}
            className="p-3 bg-primary hover:bg-primary/90 rounded-full transition-colors"
            title={isPlaying ? '暂停' : '播放'}
          >
            {isPlaying ? (
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>

          <button
            onClick={playNext}
            className="p-2 hover:bg-gray-800 rounded-full transition-colors"
            title="下一首"
          >
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" />
            </svg>
          </button>
        </div>

        {/* Time */}
        <div className="text-xs text-gray-400 w-24 text-right">
          {formatTime(currentTime)} / {formatTime(duration || currentMedia.duration || 0)}
        </div>

        {/* Close Button */}
        <button
          onClick={() => setCurrentMedia(null)}
          className="p-2 hover:bg-gray-800 rounded-full transition-colors ml-2"
          title="关闭播放器"
        >
          <svg className="w-5 h-5 text-gray-400 hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  )
}
