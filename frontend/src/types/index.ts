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

export type PlayMode = 'sequence' | 'random' | 'loop' | 'single-loop'
