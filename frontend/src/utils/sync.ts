import { api } from './api'
import type { MediaItem } from '../types'
import { db } from '../db/database'

export interface SyncFavoritesData {
  id: string
  url: string
  title: string
  thumbnail?: string
  duration?: number
  source: string
  addedAt: string
}

export interface SyncHistoryData {
  id: string
  url: string
  title: string
  thumbnail?: string
  duration?: number
  source: string
  position: number
  playedAt: string
}

export interface SyncPlaylistData {
  id: string
  name: string
  items: MediaItem[]
  createdAt: string
}

export interface SyncRequest {
  favorites: SyncFavoritesData[]
  history: SyncHistoryData[]
  playlists: SyncPlaylistData[]
}

export interface SyncResponse {
  favorites: SyncFavoritesData[]
  history: SyncHistoryData[]
  playlists: SyncPlaylistData[]
  merged: boolean
}

// Convert local IndexedDB data to sync format
async function prepareLocalData(): Promise<SyncRequest> {
  const favorites = await db.favorites.toArray()
  const history = await db.history.toArray()
  const playlists = await db.playlists.toArray()
  
  return {
    favorites: favorites.map(f => ({
      id: f.id,
      url: f.url,
      title: f.title,
      thumbnail: f.thumbnail,
      duration: f.duration,
      source: f.source,
      addedAt: f.addedAt.toISOString(),
    })),
    history: history.map(h => ({
      id: h.id,
      url: h.url,
      title: h.title,
      thumbnail: h.thumbnail,
      duration: h.duration,
      source: h.source,
      position: h.position,
      playedAt: h.playedAt.toISOString(),
    })),
    playlists: playlists.map(p => ({
      id: p.id,
      name: p.name,
      items: p.items,
      createdAt: p.createdAt.toISOString(),
    })),
  }
}

// Apply server data to local IndexedDB
async function applyServerData(data: SyncResponse): Promise<void> {
  // Clear existing data
  await db.favorites.clear()
  await db.history.clear()
  await db.playlists.clear()
  
  // Insert merged data
  if (data.favorites.length > 0) {
    await db.favorites.bulkAdd(
      data.favorites.map(f => ({
        id: f.id,
        url: f.url,
        title: f.title,
        thumbnail: f.thumbnail,
        duration: f.duration,
        source: f.source as MediaItem['source'],
        addedAt: new Date(f.addedAt),
      }))
    )
  }
  
  if (data.history.length > 0) {
    await db.history.bulkAdd(
      data.history.map(h => ({
        id: h.id,
        url: h.url,
        title: h.title,
        thumbnail: h.thumbnail,
        duration: h.duration,
        source: h.source as MediaItem['source'],
        position: h.position,
        playedAt: new Date(h.playedAt),
      }))
    )
  }
  
  if (data.playlists.length > 0) {
    await db.playlists.bulkAdd(
      data.playlists.map(p => ({
        id: p.id,
        name: p.name,
        items: p.items,
        createdAt: new Date(p.createdAt),
      }))
    )
  }
}

// Main sync function - push local data to server and pull merged data
export async function syncUserData(): Promise<{ success: boolean; message: string }> {
  try {
    const localData = await prepareLocalData()
    
    const response = await api.post<SyncResponse>('/api/auth/sync', localData)
    
    await applyServerData(response)
    
    return { success: true, message: '数据同步成功' }
  } catch (error) {
    console.error('Sync failed:', error)
    const message = error instanceof Error ? error.message : '数据同步失败'
    return { success: false, message }
  }
}

// Pull server data without pushing local data (for fresh login)
export async function pullServerData(): Promise<{ success: boolean; message: string }> {
  try {
    const response = await api.get<SyncResponse>('/api/auth/sync')
    
    await applyServerData(response)
    
    return { success: true, message: '数据拉取成功' }
  } catch (error) {
    console.error('Pull failed:', error)
    const message = error instanceof Error ? error.message : '数据拉取失败'
    return { success: false, message }
  }
}