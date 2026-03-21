export interface MediaItem {
  id: string
  url: string
  title: string
  thumbnail?: string
  duration?: number
  source: 'youtube' | 'bilibili' | 'netease' | 'other'
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
  source: 'youtube' | 'bilibili' | 'netease' | 'other'
  position: number
  playedAt: Date
}

export type PlayMode = 'sequence' | 'random' | 'loop' | 'single-loop'

export interface User {
  id: string
  username: string
  created_at: string
}