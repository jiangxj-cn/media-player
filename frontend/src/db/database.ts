import Dexie, { type Table } from 'dexie'
import type { MediaItem, Playlist } from '../types'

class MediaDatabase extends Dexie {
  favorites!: Table<MediaItem & { addedAt: Date }>
  history!: Table<MediaItem & { position: number; playedAt: Date }>
  playlists!: Table<Playlist>

  constructor() {
    super('MediaPlayerDB')
    this.version(1).stores({
      favorites: 'id, source, addedAt',
      history: 'id, source, playedAt',
      playlists: 'id, name'
    })
  }
}

export const db = new MediaDatabase()
