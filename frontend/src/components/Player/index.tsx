import { useEffect, useRef } from 'react'
import Plyr from 'plyr'
import 'plyr/dist/plyr.css'
import Hls from 'hls.js'
import { usePlayerStore } from '../../stores/playerStore'
import type { MediaItem } from '../../types'

interface PlayerProps {
  media: MediaItem | null
  onPlayStateChange?: (isPlaying: boolean) => void
  onTimeUpdate?: (currentTime: number, duration: number) => void
}

export default function Player({ media, onPlayStateChange, onTimeUpdate }: PlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const playerRef = useRef<Plyr | null>(null)
  const hlsRef = useRef<Hls | null>(null)
  const { togglePlay, isPlaying, playNext, saveProgress, getProgress } = usePlayerStore()
  const hasLoadedProgress = useRef(false)

  useEffect(() => {
    if (!videoRef.current || !media) return

    const video = videoRef.current

    // Destroy existing player
    if (playerRef.current) {
      playerRef.current.destroy()
    }

    // Destroy existing HLS instance
    if (hlsRef.current) {
      hlsRef.current.destroy()
    }

    // Initialize HLS if needed
    if (media.url.includes('.m3u8') || media.url.includes('hls')) {
      const hls = new Hls()
      hlsRef.current = hls
      hls.loadSource(media.url)
      hls.attachMedia(video)
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        void video.play()
      })
    }

    // Initialize Plyr
    playerRef.current = new Plyr(video, {
      controls: [
        'play-large',
        'play',
        'progress',
        'current-time',
        'mute',
        'volume',
        'settings',
        'pip',
        'airplay',
        'fullscreen'
      ],
      settings: ['quality', 'speed'],
      speed: { selected: 1, options: [0.5, 0.75, 1, 1.25, 1.5, 2] }
    })

    const player = playerRef.current

    // Sync play state
    player.on('play', () => {
      if (!isPlaying) togglePlay()
      onPlayStateChange?.(true)
    })

    player.on('pause', () => {
      if (isPlaying) togglePlay()
      onPlayStateChange?.(false)
    })

    player.on('timeupdate', () => {
      const currentTime = player.currentTime
      const duration = player.duration
      
      // 发送时间更新事件给 MiniPlayer
      window.dispatchEvent(new CustomEvent('player:timeupdate', {
        detail: { currentTime, duration }
      }))
      
      // 保存播放进度（每 5 秒保存一次）
      if (currentTime > 0 && Math.floor(currentTime) % 5 === 0) {
        saveProgress(media.id, currentTime)
      }
      
      onTimeUpdate?.(currentTime, duration)
    })

    player.on('ended', () => {
      playNext()
    })

    // 恢复上次的播放位置
    if (!hasLoadedProgress.current && media.id) {
      const savedProgress = getProgress(media.id)
      if (savedProgress > 0 && savedProgress < player.duration - 5) {
        player.currentTime = savedProgress
        hasLoadedProgress.current = true
      }
    }

    return () => {
      // 保存最终进度
      if (media && playerRef.current) {
        saveProgress(media.id, playerRef.current.currentTime)
      }
      
      player.destroy()
      if (hlsRef.current) {
        hlsRef.current.destroy()
      }
    }
  }, [media?.url])

  // Sync isPlaying state with player
  useEffect(() => {
    if (!playerRef.current || !media) return
    
    if (isPlaying && playerRef.current.paused) {
      void playerRef.current.play()
    } else if (!isPlaying && !playerRef.current.paused) {
      playerRef.current.pause()
    }
  }, [isPlaying, media])

  // 监听 seek 事件（来自歌词点击或 MiniPlayer 拖拽）
  useEffect(() => {
    const handleSeek = (e: Event) => {
      const customEvent = e as CustomEvent<{ time: number }>
      if (playerRef.current && customEvent.detail.time !== undefined) {
        playerRef.current.currentTime = customEvent.detail.time
      }
    }
    
    window.addEventListener('player:seek', handleSeek)
    return () => window.removeEventListener('player:seek', handleSeek)
  }, [])

  // 重置进度加载标志当媒体改变
  useEffect(() => {
    hasLoadedProgress.current = false
  }, [media?.id])

  if (!media) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900 rounded-lg min-h-[400px]">
        <div className="text-center text-gray-400">
          <svg className="w-20 h-20 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-xl">选择一首歌曲或视频开始播放</p>
        </div>
      </div>
    )
  }

  const isAudio = media.source === 'netease' || media.url.endsWith('.mp3')

  return (
    <div className="w-full">
      <div className={`relative ${isAudio ? 'bg-gray-800 rounded-lg p-8' : ''}`}>
        {isAudio ? (
          <div className="flex flex-col items-center">
            {media.thumbnail && (
              <img
                src={media.thumbnail}
                alt={media.title}
                className="w-48 h-48 object-cover rounded-lg shadow-lg mb-6"
              />
            )}
            <audio ref={videoRef} className="w-full">
              <source src={media.url} type="audio/mpeg" />
            </audio>
          </div>
        ) : (
          <video
            ref={videoRef}
            className="w-full rounded-lg"
            poster={media.thumbnail}
            playsInline
          >
            <source src={media.url} type="video/mp4" />
          </video>
        )}
      </div>
      <div className="mt-4">
        <h2 className="text-xl font-bold text-white">{media.title}</h2>
        <p className="text-gray-400 text-sm mt-1">来源：{media.source}</p>
      </div>
    </div>
  )
}
