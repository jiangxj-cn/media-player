export interface MediaItem {
  id: string
  url: string
  title: string
  thumbnail?: string
  duration?: number
  source: 'youtube' | 'bilibili' | 'netease' | 'custom' | 'other'
  embedUrl?: string  // iframe 嵌入地址
  useEmbed?: boolean  // 是否使用 iframe 播放
  pipedUrl?: string  // Piped 代理链接（用于中国大陆访问 YouTube）
}

export interface Playlist {
  id: string
  name: string
  items: MediaItem[]
  createdAt: Date
}

export interface HistoryItem {
  id: string
  url: string
  title: string
  thumbnail?: string
  duration?: number
  source: 'youtube' | 'bilibili' | 'netease' | 'custom' | 'other'
  position: number
  playedAt: Date
  embedUrl?: string
  useEmbed?: boolean
  pipedUrl?: string  // Piped 代理链接
}

export type PlayMode = 'sequence' | 'random' | 'loop' | 'single-loop'

export interface User {
  id: string
  username: string
  created_at: string
}