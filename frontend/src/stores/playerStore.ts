import { create } from 'zustand'
import type { MediaItem, PlayMode } from '../types'

interface PlayerState {
  currentMedia: MediaItem | null
  playlist: MediaItem[]
  playMode: PlayMode
  isPlaying: boolean
  setCurrentMedia: (media: MediaItem | null) => void
  setPlaylist: (items: MediaItem[]) => void
  setPlayMode: (mode: PlayMode) => void
  togglePlay: () => void
}

export const usePlayerStore = create<PlayerState>((set) => ({
  currentMedia: null,
  playlist: [],
  playMode: 'sequence',
  isPlaying: false,
  setCurrentMedia: (media) => set({ currentMedia: media }),
  setPlaylist: (items) => set({ playlist: items }),
  setPlayMode: (mode) => set({ playMode: mode }),
  togglePlay: () => set((s) => ({ isPlaying: !s.isPlaying }))
}))
