import { useState, useEffect, useRef, useMemo } from 'react'
import { usePlayerStore } from '../../stores/playerStore'
import { api } from '../../utils/api'

interface LyricLine {
  time: number // 秒
  text: string
}

interface LyricPanelProps {
  mediaId: string
  currentTime: number
}

// 解析 LRC 格式歌词
function parseLRC(lrcText: string): LyricLine[] {
  const lines: LyricLine[] = []
  const lineRegex = /\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)/g
  
  let match
  while ((match = lineRegex.exec(lrcText)) !== null) {
    const minutes = parseInt(match[1], 10)
    const seconds = parseInt(match[2], 10)
    const milliseconds = parseInt(match[3].padEnd(3, '0'), 10)
    const time = minutes * 60 + seconds + milliseconds / 1000
    const text = match[4].trim()
    
    if (text) {
      lines.push({ time, text })
    }
  }
  
  return lines.sort((a, b) => a.time - b.time)
}

export default function LyricPanel({ mediaId, currentTime }: LyricPanelProps) {
  const [lyrics, setLyrics] = useState<LyricLine[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const { currentMedia } = usePlayerStore()
  
  // 当前高亮的歌词索引
  const activeIndex = useMemo(() => {
    if (lyrics.length === 0) return -1
    
    for (let i = lyrics.length - 1; i >= 0; i--) {
      if (currentTime >= lyrics[i].time) {
        return i
      }
    }
    return 0
  }, [lyrics, currentTime])
  
  // 加载歌词
  useEffect(() => {
    if (!mediaId) {
      setLyrics([])
      return
    }
    
    const fetchLyrics = async () => {
      setLoading(true)
      setError(null)
      
      try {
        // 调用后端 API 获取歌词
        const response = await api.get<{ lrc?: string }>(`/api/lyrics?mediaId=${mediaId}`)
        
        if (response.lrc) {
          const parsed = parseLRC(response.lrc)
          setLyrics(parsed)
        } else {
          setLyrics([])
        }
      } catch (err) {
        console.error('Failed to fetch lyrics:', err)
        setError('歌词加载失败')
        setLyrics([])
      } finally {
        setLoading(false)
      }
    }
    
    fetchLyrics()
  }, [mediaId])
  
  // 自动滚动到当前歌词
  useEffect(() => {
    if (activeIndex === -1 || !containerRef.current) return
    
    const container = containerRef.current
    const activeElement = container.querySelector(`[data-index="${activeIndex}"]`)
    
    if (activeElement) {
      const containerHeight = container.clientHeight
      const elementTop = (activeElement as HTMLElement).offsetTop
      const elementHeight = (activeElement as HTMLElement).offsetHeight
      
      // 让当前歌词保持在容器中间
      const scrollTop = elementTop - containerHeight / 2 + elementHeight / 2
      
      container.scrollTo({
        top: Math.max(0, scrollTop),
        behavior: 'smooth'
      })
    }
  }, [activeIndex])
  
  // 点击歌词跳转播放位置
  const handleLyricClick = (time: number) => {
    // 触发播放器跳转事件
    window.dispatchEvent(new CustomEvent('player:seek', { detail: { time } }))
  }
  
  if (!currentMedia) {
    return null
  }
  
  return (
    <div className="h-full flex flex-col bg-gray-900/50 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-800">
        <h3 className="font-medium text-white">歌词</h3>
      </div>
      
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto px-4 py-6 space-y-4"
      >
        {loading && (
          <div className="text-center text-gray-400 py-8">
            <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto mb-2" />
            <p className="text-sm">加载歌词中...</p>
          </div>
        )}
        
        {error && (
          <div className="text-center text-gray-400 py-8">
            <p className="text-sm">{error}</p>
          </div>
        )}
        
        {!loading && !error && lyrics.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            <p className="text-sm">暂无歌词</p>
          </div>
        )}
        
        {!loading && !error && lyrics.map((line, index) => (
          <div
            key={index}
            data-index={index}
            onClick={() => handleLyricClick(line.time)}
            className={`text-center py-2 px-4 rounded-lg cursor-pointer transition-all duration-300 ${
              index === activeIndex
                ? 'text-primary text-lg font-medium scale-105'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            {line.text}
          </div>
        ))}
      </div>
    </div>
  )
}
