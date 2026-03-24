/**
 * 视频质量选择器组件
 * 允许用户选择不同的视频质量
 */

import { useState, useEffect, useCallback, memo } from 'react'
import { formatFileSize, type VideoQuality } from '../../utils/helpers'

interface VideoFormat {
  format_id: string
  ext: string
  resolution: string
  height: number
  fps?: number
  filesize?: number
  vcodec?: string
  acodec?: string
  url?: string
}

interface QualitySelectorProps {
  videoUrl: string
  currentQuality?: VideoQuality
  onQualityChange: (format: VideoFormat) => void
  onClose?: () => void
}

function QualitySelector({ 
  videoUrl, 
  onQualityChange,
  onClose
}: QualitySelectorProps) {
  const [formats, setFormats] = useState<VideoFormat[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedFormat, setSelectedFormat] = useState<string>('')

  // 获取可用格式
  const fetchFormats = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/formats?url=${encodeURIComponent(videoUrl)}`)
      if (!response.ok) {
        throw new Error('获取格式失败')
      }
      
      const data = await response.json()
      setFormats(data.formats || [])
      
      // 默认选中最高质量
      if (data.formats?.length > 0) {
        setSelectedFormat(data.formats[0].format_id)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : '未知错误')
    } finally {
      setLoading(false)
    }
  }, [videoUrl])

  useEffect(() => {
    fetchFormats()
  }, [fetchFormats])

  const handleSelect = (format: VideoFormat) => {
    setSelectedFormat(format.format_id)
    onQualityChange(format)
  }

  // 将格式分组
  const groupedFormats = formats.reduce((acc, format) => {
    let quality = '其他'
    if (format.height >= 1080) quality = '高清 1080P+'
    else if (format.height >= 720) quality = '高清 720P'
    else if (format.height >= 480) quality = '标清 480P'
    else if (format.height >= 360) quality = '流畅 360P'
    
    if (!acc[quality]) acc[quality] = []
    acc[quality].push(format)
    return acc
  }, {} as Record<string, VideoFormat[]>)

  if (loading) {
    return (
      <div className="p-4 text-center">
        <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto mb-2" />
        <p className="text-gray-400 text-sm">加载格式中...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 text-center">
        <p className="text-red-400 text-sm mb-2">{error}</p>
        <button 
          onClick={fetchFormats}
          className="text-primary text-sm hover:underline"
        >
          重试
        </button>
      </div>
    )
  }

  if (formats.length === 0) {
    return (
      <div className="p-4 text-center text-gray-400 text-sm">
        没有可用的格式选项
      </div>
    )
  }

  return (
    <div className="bg-gray-900 rounded-lg overflow-hidden max-h-80 overflow-y-auto">
      <div className="sticky top-0 bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between">
        <h3 className="text-sm font-medium">选择画质</h3>
        {onClose && (
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      <div className="p-2">
        {Object.entries(groupedFormats).map(([quality, items]) => (
          <div key={quality} className="mb-2">
            <div className="text-xs text-gray-500 px-2 py-1">{quality}</div>
            {items.map((format) => (
              <button
                key={format.format_id}
                onClick={() => handleSelect(format)}
                className={`
                  w-full text-left px-3 py-2 rounded-lg mb-1 transition-colors
                  ${selectedFormat === format.format_id 
                    ? 'bg-primary/20 text-primary' 
                    : 'hover:bg-gray-800 text-gray-300'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">
                      {format.resolution}
                    </span>
                    {format.fps && (
                      <span className="text-xs text-gray-500">
                        {format.fps}fps
                      </span>
                    )}
                    {format.vcodec && format.vcodec !== 'none' && (
                      <span className="text-xs px-1.5 py-0.5 bg-gray-700 rounded">
                        {format.ext}
                      </span>
                    )}
                  </div>
                  {format.filesize && (
                    <span className="text-xs text-gray-500">
                      {formatFileSize(format.filesize)}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

export default memo(QualitySelector)