import { useEffect, useRef } from 'react'
import Plyr from 'plyr'
import 'plyr/dist/plyr.css'
import Hls from 'hls.js'
import { usePlayerStore } from '../../stores/playerStore'
import type { MediaItem } from '../../types'

interface PlayerProps {
  media: MediaItem | null
}

export default function Player({ media }: PlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const playerRef = useRef<Plyr | null>(null)
  const { togglePlay, isPlaying } = usePlayerStore()

  useEffect(() => {
    if (!videoRef.current || !media) return

    const video = videoRef.current

    // Initialize Plyr
    playerRef.current = new Plyr(video, {
      controls: ['play-large', 'play', 'progress', 'current-time', 'mute', 'volume', 'captions', 'settings', 'pip', 'airplay', 'fullscreen'],
    })

    // Handle HLS streams
    const source = media.url
    if (source.includes('.m3u8') || source.includes('hls')) {
      const hls = new Hls()
      hls.loadSource(source)
      hls.attachMedia(video)
    }

    // Sync play state
    playerRef.current.on('play', () => {
      if (!isPlaying) togglePlay()
    })

    playerRef.current.on('pause', () => {
      if (isPlaying) togglePlay()
    })

    return () => {
      playerRef.current?.destroy()
    }
  }, [media])

  if (!media) {
    return (
      <div className="flex items-center justify-center h-full bg-bg-card rounded-lg">
        <div className="text-center text-gray-500">
          <p className="text-xl">选择一首歌曲或视频开始播放</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      <video
        ref={videoRef}
        className="w-full rounded-lg"
        poster={media.thumbnail}
      >
        <source src={media.url} type="video/mp4" />
      </video>
      <div className="mt-4">
        <h2 className="text-xl font-bold">{media.title}</h2>
        <p className="text-gray-400 text-sm mt-1">来源：{media.source}</p>
      </div>
    </div>
  )
}
