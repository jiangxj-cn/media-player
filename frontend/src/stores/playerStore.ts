import { create } from 'zustand'
import type { MediaItem, PlayMode, HistoryItem } from '../types'
import { db } from '../db/database'
import { syncUserData } from '../utils/sync'

interface PlayerState {
  // 现有
  currentMedia: MediaItem | null
  playlist: MediaItem[]
  playMode: PlayMode
  isPlaying: boolean
  
  // 新增
  favorites: MediaItem[]
  history: HistoryItem[]
  progressMap: Record<string, number> // 记录每个媒体的播放位置
  
  // 同步状态
  isSyncing: boolean
  lastSyncTime: Date | null
  
  // 现有 Actions
  setCurrentMedia: (media: MediaItem | null) => void
  setPlaylist: (items: MediaItem[]) => void
  setPlayMode: (mode: PlayMode) => void
  togglePlay: () => void
  
  // 新增 Actions
  addToPlaylist: (item: MediaItem) => void
  removeFromPlaylist: (id: string) => void
  clearPlaylist: () => void
  addToFavorites: (item: MediaItem) => void
  removeFromFavorites: (id: string) => void
  addToHistory: (item: MediaItem, position: number) => void
  clearHistory: () => void
  playNext: () => void
  playPrevious: () => void
  saveProgress: (mediaId: string, position: number) => void
  getProgress: (mediaId: string) => number
  
  // 同步 Actions
  loadFromDB: () => Promise<void>
  syncWithServer: () => Promise<{ success: boolean; message: string }>
  setFavorites: (items: MediaItem[]) => void
  setHistory: (items: HistoryItem[]) => void
}

export const usePlayerStore = create<PlayerState>((set, get) => ({
  currentMedia: null,
  playlist: [],
  playMode: 'sequence',
  isPlaying: false,
  favorites: [],
  history: [],
  progressMap: {},
  isSyncing: false,
  lastSyncTime: null,
  
  // 现有 Actions
  setCurrentMedia: (media) => {
    set({ currentMedia: media })
    // 注意：实际播放位置恢复由 Player 组件处理
  },
  setPlaylist: (items) => set({ playlist: items }),
  setPlayMode: (mode) => set({ playMode: mode }),
  togglePlay: () => set((s) => ({ isPlaying: !s.isPlaying })),
  
  // 新增 Actions
  addToPlaylist: (item) => set((s) => {
    if (s.playlist.find(i => i.id === item.id)) {
      return s
    }
    return { playlist: [...s.playlist, item] }
  }),
  
  removeFromPlaylist: (id) => set((s) => ({
    playlist: s.playlist.filter(i => i.id !== id)
  })),
  
  clearPlaylist: () => set({ playlist: [] }),
  
  addToFavorites: async (item) => {
    const { favorites } = get()
    if (favorites.find(i => i.id === item.id)) {
      return
    }
    
    const newItem = { ...item, addedAt: new Date() }
    set({ favorites: [...favorites, item] })
    
    // Persist to IndexedDB
    try {
      await db.favorites.add(newItem as MediaItem & { addedAt: Date })
    } catch (error) {
      console.error('Failed to save favorite to DB:', error)
    }
  },
  
  removeFromFavorites: async (id) => {
    set((s) => ({
      favorites: s.favorites.filter(i => i.id !== id)
    }))
    
    // Remove from IndexedDB
    try {
      await db.favorites.delete(id)
    } catch (error) {
      console.error('Failed to remove favorite from DB:', error)
    }
  },
  
  addToHistory: async (item, position) => {
    const { history } = get()
    const newItem: HistoryItem = {
      ...item,
      position,
      playedAt: new Date()
    }
    
    // 移除已存在的相同记录，添加到开头
    const filtered = history.filter(i => i.id !== item.id)
    const newHistory = [newItem, ...filtered].slice(0, 100) // 最多保留 100 条
    set({ history: newHistory })
    
    // Persist to IndexedDB
    try {
      await db.history.where('id').equals(item.id).delete()
      await db.history.add({ ...newItem, playedAt: new Date() })
    } catch (error) {
      console.error('Failed to save history to DB:', error)
    }
  },
  
  clearHistory: async () => {
    set({ history: [] })
    
    // Clear IndexedDB
    try {
      await db.history.clear()
    } catch (error) {
      console.error('Failed to clear history from DB:', error)
    }
  },
  
  playNext: () => {
    const { currentMedia, playlist, playMode } = get()
    if (!currentMedia || playlist.length === 0) return
    
    const currentIndex = playlist.findIndex(i => i.id === currentMedia.id)
    let nextIndex: number
    
    if (playMode === 'random') {
      nextIndex = Math.floor(Math.random() * playlist.length)
    } else if (playMode === 'single-loop') {
      nextIndex = currentIndex
    } else {
      nextIndex = currentIndex + 1
      if (nextIndex >= playlist.length) {
        nextIndex = playMode === 'loop' ? 0 : currentIndex
      }
    }
    
    if (nextIndex !== currentIndex) {
      set({ currentMedia: playlist[nextIndex] })
    }
  },
  
  playPrevious: () => {
    const { currentMedia, playlist, playMode } = get()
    if (!currentMedia || playlist.length === 0) return
    
    const currentIndex = playlist.findIndex(i => i.id === currentMedia.id)
    let prevIndex = currentIndex - 1
    
    if (prevIndex < 0) {
      prevIndex = playMode === 'loop' ? playlist.length - 1 : 0
    }
    
    if (prevIndex !== currentIndex) {
      set({ currentMedia: playlist[prevIndex] })
    }
  },
  
  saveProgress: (mediaId, position) => {
    const { progressMap } = get()
    set({
      progressMap: {
        ...progressMap,
        [mediaId]: position
      }
    })
    
    // 保存到 localStorage 作为持久化
    try {
      const saved = localStorage.getItem('player_progress')
      const progressData = saved ? JSON.parse(saved) : {}
      progressData[mediaId] = position
      localStorage.setItem('player_progress', JSON.stringify(progressData))
    } catch (error) {
      console.error('Failed to save progress to localStorage:', error)
    }
  },
  
  getProgress: (mediaId) => {
    const { progressMap } = get()
    return progressMap[mediaId] || 0
  },
  
  // 同步 Actions
  loadFromDB: async () => {
    try {
      const [favorites, history, playlists] = await Promise.all([
        db.favorites.toArray(),
        db.history.toArray(),
        db.playlists.toArray(),
      ])
      
      // 从 localStorage 加载进度数据
      let progressMap: Record<string, number> = {}
      try {
        const saved = localStorage.getItem('player_progress')
        if (saved) {
          progressMap = JSON.parse(saved)
        }
      } catch (error) {
        console.error('Failed to load progress from localStorage:', error)
      }
      
      set({
        favorites: favorites.map(f => ({
          id: f.id,
          url: f.url,
          title: f.title,
          thumbnail: f.thumbnail,
          duration: f.duration,
          source: f.source,
        })),
        history: history.map(h => ({
          id: h.id,
          url: h.url,
          title: h.title,
          thumbnail: h.thumbnail,
          duration: h.duration,
          source: h.source,
          position: h.position,
          playedAt: h.playedAt,
        })),
        progressMap,
      })
      
      // Set first playlist as current if exists
      if (playlists.length > 0) {
        set({ playlist: playlists[0].items })
      }
    } catch (error) {
      console.error('Failed to load from DB:', error)
    }
  },
  
  syncWithServer: async () => {
    const { isSyncing } = get()
    if (isSyncing) {
      return { success: false, message: '正在同步中...' }
    }
    
    set({ isSyncing: true })
    
    try {
      const result = await syncUserData()
      
      if (result.success) {
        // Reload data from DB after sync
        await get().loadFromDB()
        set({ lastSyncTime: new Date() })
      }
      
      set({ isSyncing: false })
      return result
    } catch (error) {
      set({ isSyncing: false })
      const message = error instanceof Error ? error.message : '同步失败'
      return { success: false, message }
    }
  },
  
  setFavorites: (items) => set({ favorites: items }),
  setHistory: (items) => set({ history: items }),
}))