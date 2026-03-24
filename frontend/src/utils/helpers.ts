/**
 * 防抖函数 - 用于搜索输入优化
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null
  
  return function(this: any, ...args: Parameters<T>) {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    
    timeoutId = setTimeout(() => {
      fn.apply(this, args)
      timeoutId = null
    }, delay)
  }
}

/**
 * 节流函数 - 用于滚动事件优化
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0
  
  return function(this: any, ...args: Parameters<T>) {
    const now = Date.now()
    
    if (now - lastCall >= delay) {
      fn.apply(this, args)
      lastCall = now
    }
  }
}

/**
 * 格式化时长
 */
export function formatDuration(seconds: number): string {
  if (!seconds || isNaN(seconds)) return '0:00'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes) return '未知'
  
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  
  return `${size.toFixed(1)} ${units[i]}`
}

/**
 * 解析时长字符串 (如 "3:45" -> 225)
 */
export function parseDuration(duration: string): number {
  if (!duration) return 0
  const parts = duration.split(':').map(Number)
  if (parts.length === 2) return parts[0] * 60 + parts[1]
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2]
  return parseInt(duration) || 0
}

/**
 * 检测视频平台
 */
export function detectVideoPlatform(url: string): string {
  const urlLower = url.toLowerCase()
  
  if (urlLower.includes('bilibili.com') || urlLower.includes('b23.tv')) return 'bilibili'
  if (urlLower.includes('douyin.com') || urlLower.includes('iesdouyin.com')) return 'douyin'
  if (urlLower.includes('ixigua.com')) return 'ixigua'
  if (urlLower.includes('youtube.com') || urlLower.includes('youtu.be')) return 'youtube'
  if (urlLower.includes('tiktok.com')) return 'tiktok'
  
  return 'unknown'
}

/**
 * 获取平台显示名称
 */
export function getPlatformDisplayName(platform: string): string {
  const names: Record<string, string> = {
    bilibili: 'B站',
    douyin: '抖音',
    ixigua: '西瓜视频',
    youtube: 'YouTube',
    tiktok: 'TikTok',
    netease: '网易云',
    unknown: '未知'
  }
  return names[platform] || platform
}

/**
 * 懒加载图片
 */
export function createIntersectionObserver(
  callback: (entry: IntersectionObserverEntry) => void,
  options?: IntersectionObserverInit
): IntersectionObserver {
  return new IntersectionObserver((entries) => {
    entries.forEach(callback)
  }, {
    rootMargin: '100px',
    threshold: 0.1,
    ...options
  })
}

/**
 * 检测是否为移动设备
 */
export function isMobileDevice(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  )
}

/**
 * 检测是否支持触摸
 */
export function isTouchDevice(): boolean {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0
}

/**
 * 本地存储封装
 */
export const storage = {
  get<T>(key: string, defaultValue: T): T {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue
    } catch {
      return defaultValue
    }
  },
  
  set<T>(key: string, value: T): void {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch (e) {
      console.error('Failed to save to localStorage:', e)
    }
  },
  
  remove(key: string): void {
    localStorage.removeItem(key)
  }
}

/**
 * 视频质量等级
 */
export const VIDEO_QUALITIES = {
  best: { label: '最高', height: 1080 },
  high: { label: '高清 1080P', height: 1080 },
  medium: { label: '高清 720P', height: 720 },
  low: { label: '标清 480P', height: 480 },
  audio: { label: '仅音频', height: 0 }
} as const

export type VideoQuality = keyof typeof VIDEO_QUALITIES