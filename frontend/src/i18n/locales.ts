/**
 * 国际化配置
 * 支持中英文语言切换
 */

export type Locale = 'zh' | 'en'

interface LocaleStrings {
  [key: string]: string | LocaleStrings
}

// 中文语言包
export const zhCN: LocaleStrings = {
  // 通用
  common: {
    search: '搜索',
    cancel: '取消',
    confirm: '确认',
    save: '保存',
    delete: '删除',
    edit: '编辑',
    loading: '加载中...',
    error: '错误',
    success: '成功',
    retry: '重试',
    close: '关闭',
    more: '更多',
    all: '全部',
    none: '无',
  },
  
  // 导航
  nav: {
    home: '首页',
    playlist: '播放列表',
    favorites: '收藏',
    history: '历史',
    settings: '设置',
  },
  
  // 搜索
  search: {
    placeholder: '搜索音乐、视频...',
    hint: '输入关键词搜索',
    noResults: '没有找到结果',
    searching: '搜索中...',
    recentSearches: '最近搜索',
    clearHistory: '清除历史',
  },
  
  // 播放器
  player: {
    play: '播放',
    pause: '暂停',
    next: '下一首',
    previous: '上一首',
    volume: '音量',
    mute: '静音',
    fullscreen: '全屏',
    exitFullscreen: '退出全屏',
    pip: '画中画',
    speed: '倍速',
    quality: '画质',
    subtitles: '字幕',
    noMedia: '选择一首歌曲或视频开始播放',
    nowPlaying: '正在播放',
  },
  
  // 视频
  video: {
    quality: {
      best: '最高画质',
      high: '高清 1080P',
      medium: '高清 720P',
      low: '标清 480P',
      audio: '仅音频',
    },
    source: '来源',
    duration: '时长',
    views: '播放量',
    uploadDate: '上传时间',
  },
  
  // 播放列表
  playlist: {
    title: '播放列表',
    empty: '播放列表为空',
    add: '添加到播放列表',
    remove: '从播放列表移除',
    clear: '清空播放列表',
    shuffle: '随机播放',
    playAll: '播放全部',
  },
  
  // 收藏
  favorites: {
    title: '我的收藏',
    empty: '还没有收藏任何内容',
    add: '收藏',
    remove: '取消收藏',
  },
  
  // 历史
  history: {
    title: '播放历史',
    empty: '暂无播放历史',
    clear: '清除历史',
    clearConfirm: '确定要清除所有播放历史吗？',
  },
  
  // 用户
  user: {
    login: '登录',
    register: '注册',
    logout: '退出登录',
    guest: '访客模式',
    loggedIn: '已登录',
    username: '用户名',
    password: '密码',
    email: '邮箱',
  },
  
  // 设置
  settings: {
    title: '设置',
    theme: '主题',
    darkMode: '深色模式',
    lightMode: '浅色模式',
    autoMode: '跟随系统',
    language: '语言',
    chinese: '中文',
    english: 'English',
    autoPlay: '自动播放',
    defaultQuality: '默认画质',
    proxy: '代理播放',
  },
  
  // 错误信息
  errors: {
    networkError: '网络错误，请检查网络连接',
    videoUnavailable: '视频不可用',
    privateVideo: '这是私密视频',
    unsupportedSource: '不支持的视频源',
    extractFailed: '解析失败',
    loginRequired: '请先登录',
    sessionExpired: '登录已过期，请重新登录',
  },
  
  // 平台名称
  platforms: {
    bilibili: 'B站',
    douyin: '抖音',
    ixigua: '西瓜视频',
    youtube: 'YouTube',
    tiktok: 'TikTok',
    netease: '网易云',
    unknown: '未知',
  },
}

// 英文语言包
export const enUS: LocaleStrings = {
  // Common
  common: {
    search: 'Search',
    cancel: 'Cancel',
    confirm: 'Confirm',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    retry: 'Retry',
    close: 'Close',
    more: 'More',
    all: 'All',
    none: 'None',
  },
  
  // Navigation
  nav: {
    home: 'Home',
    playlist: 'Playlist',
    favorites: 'Favorites',
    history: 'History',
    settings: 'Settings',
  },
  
  // Search
  search: {
    placeholder: 'Search music, videos...',
    hint: 'Enter keywords to search',
    noResults: 'No results found',
    searching: 'Searching...',
    recentSearches: 'Recent searches',
    clearHistory: 'Clear history',
  },
  
  // Player
  player: {
    play: 'Play',
    pause: 'Pause',
    next: 'Next',
    previous: 'Previous',
    volume: 'Volume',
    mute: 'Mute',
    fullscreen: 'Fullscreen',
    exitFullscreen: 'Exit Fullscreen',
    pip: 'Picture in Picture',
    speed: 'Speed',
    quality: 'Quality',
    subtitles: 'Subtitles',
    noMedia: 'Select a song or video to start playing',
    nowPlaying: 'Now Playing',
  },
  
  // Video
  video: {
    quality: {
      best: 'Best Quality',
      high: 'HD 1080P',
      medium: 'HD 720P',
      low: 'SD 480P',
      audio: 'Audio Only',
    },
    source: 'Source',
    duration: 'Duration',
    views: 'Views',
    uploadDate: 'Upload Date',
  },
  
  // Playlist
  playlist: {
    title: 'Playlist',
    empty: 'Playlist is empty',
    add: 'Add to playlist',
    remove: 'Remove from playlist',
    clear: 'Clear playlist',
    shuffle: 'Shuffle',
    playAll: 'Play All',
  },
  
  // Favorites
  favorites: {
    title: 'My Favorites',
    empty: 'No favorites yet',
    add: 'Favorite',
    remove: 'Unfavorite',
  },
  
  // History
  history: {
    title: 'Play History',
    empty: 'No play history',
    clear: 'Clear History',
    clearConfirm: 'Are you sure you want to clear all history?',
  },
  
  // User
  user: {
    login: 'Login',
    register: 'Register',
    logout: 'Logout',
    guest: 'Guest Mode',
    loggedIn: 'Logged in',
    username: 'Username',
    password: 'Password',
    email: 'Email',
  },
  
  // Settings
  settings: {
    title: 'Settings',
    theme: 'Theme',
    darkMode: 'Dark Mode',
    lightMode: 'Light Mode',
    autoMode: 'System',
    language: 'Language',
    chinese: '中文',
    english: 'English',
    autoPlay: 'Auto Play',
    defaultQuality: 'Default Quality',
    proxy: 'Proxy Playback',
  },
  
  // Errors
  errors: {
    networkError: 'Network error, please check your connection',
    videoUnavailable: 'Video unavailable',
    privateVideo: 'This is a private video',
    unsupportedSource: 'Unsupported video source',
    extractFailed: 'Extraction failed',
    loginRequired: 'Please login first',
    sessionExpired: 'Session expired, please login again',
  },
  
  // Platforms
  platforms: {
    bilibili: 'Bilibili',
    douyin: 'Douyin',
    ixigua: 'iXigua',
    youtube: 'YouTube',
    tiktok: 'TikTok',
    netease: 'NetEase',
    unknown: 'Unknown',
  },
}

// 语言映射
const locales: Record<Locale, LocaleStrings> = {
  zh: zhCN,
  en: enUS,
}

/**
 * 获取翻译文本
 * @param locale 语言
 * @param key 键名 (支持点号分隔的嵌套键)
 * @param params 替换参数
 */
export function t(locale: Locale, key: string, params?: Record<string, string | number>): string {
  const keys = key.split('.')
  let value: string | LocaleStrings = locales[locale]
  
  for (const k of keys) {
    if (typeof value === 'string') break
    value = value[k] || key
  }
  
  if (typeof value !== 'string') return key
  
  // 替换参数
  if (params) {
    return Object.entries(params).reduce(
      (str, [k, v]) => str.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v)),
      value
    )
  }
  
  return value
}

/**
 * 检测浏览器语言
 */
export function detectBrowserLocale(): Locale {
  const lang = navigator.language.toLowerCase()
  if (lang.startsWith('zh')) return 'zh'
  return 'en'
}

/**
 * 获取存储的语言或检测
 */
export function getStoredLocale(): Locale {
  const stored = localStorage.getItem('locale')
  if (stored === 'zh' || stored === 'en') return stored
  return detectBrowserLocale()
}

/**
 * 存储语言设置
 */
export function setStoredLocale(locale: Locale): void {
  localStorage.setItem('locale', locale)
}