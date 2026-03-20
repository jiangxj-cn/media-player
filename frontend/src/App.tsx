import { useState } from 'react'
import Layout from './components/Layout'
import SearchBar from './components/SearchBar'
import Player from './components/Player'
import { usePlayerStore } from './stores/playerStore'
import type { MediaItem } from './types'

function App() {
  const { currentMedia, setCurrentMedia } = usePlayerStore()
  const [searchResults, setSearchResults] = useState<MediaItem[]>([])

  const handleSearch = async (query: string) => {
    // TODO: Implement actual search API call
    console.log('Searching for:', query)
    // Mock results for now
    const mockResults: MediaItem[] = [
      {
        id: '1',
        url: 'https://www.w3schools.com/html/mov_bbb.mp4',
        title: '示例视频 - ' + query,
        thumbnail: '',
        duration: 10,
        source: 'other'
      }
    ]
    setSearchResults(mockResults)
    if (mockResults.length > 0) {
      setCurrentMedia(mockResults[0])
    }
  }

  const sidebar = (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-primary">播放列表</h2>
      <div className="text-gray-400 text-sm">
        <p>暂无播放列表</p>
      </div>
      
      <h2 className="text-lg font-bold text-primary mt-6">收藏夹</h2>
      <div className="text-gray-400 text-sm">
        <p>暂无收藏</p>
      </div>
    </div>
  )

  return (
    <Layout sidebar={sidebar}>
      <div className="flex-1 flex flex-col p-6 gap-6 overflow-auto">
        {/* Search Section */}
        <div className="max-w-3xl">
          <SearchBar onSearch={handleSearch} />
        </div>

        {/* Player Section */}
        <div className="flex-1 min-h-0">
          <Player media={currentMedia} />
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="max-w-3xl">
            <h3 className="text-lg font-bold mb-3">搜索结果</h3>
            <div className="space-y-2">
              {searchResults.map((item) => (
                <div
                  key={item.id}
                  onClick={() => setCurrentMedia(item)}
                  className="flex items-center gap-4 p-3 bg-bg-card rounded-lg hover:bg-bg-secondary cursor-pointer transition-colors"
                >
                  <div className="w-16 h-12 bg-gray-700 rounded flex items-center justify-center">
                    <span className="text-xs text-gray-500">预览</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">{item.title}</h4>
                    <p className="text-sm text-gray-400">{item.source}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default App
