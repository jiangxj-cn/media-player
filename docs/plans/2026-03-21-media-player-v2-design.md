# Media Player v2.0 设计文档

> 创建日期：2026-03-21  
> 状态：已确认，待实现

---

## 一、项目概述

将现有的 Web Media Player 升级为功能完善的媒体播放应用，支持多平台搜索、播放列表管理、用户账号、PWA 离线访问。

### 核心功能

| 模块 | 功能 |
|------|------|
| 🎵 播放体验 | 播放列表、播放模式、进度记忆、歌词显示、Mini播放器 |
| 💾 收藏历史 | 收藏管理、播放历史、多播放列表 |
| 🔐 账号系统 | 注册登录、云端同步 |
| 📱 PWA | 可安装、离线访问 |
| 🐳 部署 | Docker 一键部署 |

### 关键决策

- **账号系统**：简单账号（用户名/密码），JWT 认证
- **下载功能**：浏览器下载，不占用服务器空间
- **部署方式**：PWA + Docker

---

## 二、技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Media Player v2.0                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (PWA)                                             │
│  ├── React + TypeScript + Tailwind CSS                     │
│  ├── Plyr 播放器 + HLS.js                                   │
│  ├── Service Worker (离线缓存)                              │
│  └── IndexedDB (本地收藏/历史)                              │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI)                                          │
│  ├── /api/search     多平台搜索                             │
│  ├── /api/extract    链接解析                               │
│  ├── /api/download   下载代理                               │
│  ├── /api/lyric      歌词获取                               │
│  ├── /api/auth       用户认证                               │
│  ├── /api/playlist   播放列表 CRUD                          │
│  └── /api/history    历史记录                               │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├── SQLite (用户/播放列表/历史)                            │
│  └── Redis (可选，搜索缓存)                                 │
├─────────────────────────────────────────────────────────────┤
│  Deployment                                                 │
│  └── Docker + docker-compose                                │
└─────────────────────────────────────────────────────────────┘
```

### 技术选型

| 层级 | 技术 | 理由 |
|------|------|------|
| 前端框架 | React 18 + TypeScript | PWA 生态成熟，类型安全 |
| 样式 | Tailwind CSS | 快速开发，响应式友好 |
| 播放器 | Plyr + HLS.js | 轻量，支持多格式 |
| 状态管理 | Zustand | 简单轻量 |
| 本地存储 | IndexedDB (Dexie.js) | 大容量，结构化存储 |
| 后端框架 | FastAPI | 现有基础，异步支持好 |
| 数据库 | SQLite | 简单，无需额外服务 |
| 认证 | JWT | 无状态，简单 |
| 部署 | Docker | 一键部署，环境一致 |

---

## 三、功能模块设计

### 3.1 播放体验增强

#### 播放列表
- 侧边栏显示，支持拖拽排序
- 多列表管理（创建/删除/重命名）
- 添加/移除媒体项

#### 播放模式
```typescript
type PlayMode = 'sequence' | 'random' | 'loop' | 'single-loop'
```

#### 进度记忆
```typescript
interface ProgressRecord {
  mediaId: string
  position: number      // 秒
  duration: number
  lastPlayedAt: Date
}
```

#### 歌词显示
- 支持 LRC 格式解析
- 滚动高亮当前行
- 点击歌词跳转播放位置

#### Mini 播放器
- 底部固定播放条
- 显示：缩略图、标题、播放控制
- 浏览其他页面时不中断

### 3.2 收藏与历史

#### 数据结构

```typescript
// 收藏
interface Favorite {
  id: string
  mediaUrl: string
  title: string
  thumbnail?: string
  source: 'youtube' | 'bilibili' | 'netease' | 'other'
  createdAt: Date
}

// 历史记录
interface HistoryItem {
  id: string
  mediaUrl: string
  title: string
  thumbnail?: string
  position: number        // 最后播放位置
  duration: number
  lastPlayedAt: Date
}

// 播放列表
interface Playlist {
  id: string
  name: string
  items: PlaylistItem[]
  createdAt: Date
  updatedAt: Date
}

interface PlaylistItem {
  id: string
  mediaUrl: string
  title: string
  thumbnail?: string
  source: string
  addedAt: Date
}
```

#### 同步策略
1. **本地优先**：所有操作先写入 IndexedDB
2. **登录后同步**：自动拉取云端数据，合并本地数据
3. **冲突解决**：`lastPlayedAt` / `updatedAt` 时间戳优先

### 3.3 账号系统

#### API 设计

```
POST /api/auth/register
  Body: { username: string, password: string }
  Response: { success: boolean, message: string }

POST /api/auth/login
  Body: { username: string, password: string }
  Response: { 
    success: boolean, 
    token: string, 
    user: { id, username, createdAt } 
  }

GET /api/auth/profile
  Header: Authorization: Bearer <token>
  Response: { id, username, createdAt, stats: { favorites, history } }

POST /api/auth/sync
  Header: Authorization: Bearer <token>
  Body: { favorites, history, playlists }
  Response: { merged: { favorites, history, playlists } }
```

#### 安全措施
- 密码 bcrypt 加密（cost=12）
- JWT 有效期 7 天
- Token 存储在 localStorage
- 敏感 API 需要 Authorization header

### 3.4 下载功能

#### 流程
1. 用户点击下载按钮
2. 后端 `/api/download` 代理获取媒体流
3. 设置 `Content-Disposition` 头触发浏览器下载
4. 用户在本地管理下载的文件

#### API
```
GET /api/download?url=<media_url>&format=<video|audio>
  Response: StreamingResponse with download headers
```

### 3.5 PWA 功能

#### manifest.json
```json
{
  "name": "Media Player",
  "short_name": "MediaPlayer",
  "description": "多平台视频音乐播放器",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f0f0f",
  "theme_color": "#7c3aed",
  "icons": [...]
}
```

#### Service Worker
- 缓存静态资源（JS/CSS/图片）
- 离线时显示"无网络"提示页
- 不缓存媒体流（太大）

---

## 四、UI 设计

### 4.1 布局结构

```
┌──────────────────────────────────────────────────────────┐
│  🔍 搜索栏                          👤 登录/用户头像      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────┐  ┌──────────────────────────┐  │
│  │                     │  │  📋 播放列表             │  │
│  │     🎬 播放器       │  │  ├─ 我喜欢的音乐 (23)    │  │
│  │                     │  │  ├─ 工作BGM (15)         │  │
│  │                     │  │  └─ + 新建列表           │  │
│  └─────────────────────┘  ├──────────────────────────┤  │
│  📝 歌词 (滚动)           │  ⭐ 收藏列表              │  │
│                          │  ├─ [缩略图] 歌曲名       │  │
│  ┌─────────────────────┐  │  └─ ...                  │  │
│  │ 🔍 搜索结果         │  └──────────────────────────┘  │
│  │ [卡片] [卡片] ...   │                                │
│  └─────────────────────┘                                │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  ▶️ Mini播放器: [缩略图] 正在播放 - XXX  ▶ ⏭ 🔀 🔁     │
└──────────────────────────────────────────────────────────┘
```

### 4.2 主题

**深色模式（默认）**
```css
--bg-primary: #0f0f0f
--bg-secondary: #1a1a1a
--bg-card: #1f1f1f
--text-primary: #ffffff
--text-secondary: #a0a0a0
--accent: #7c3aed (紫色)
--accent-hover: #6d28d9
```

**浅色模式**
```css
--bg-primary: #ffffff
--bg-secondary: #f5f5f5
--bg-card: #ffffff
--text-primary: #1a1a1a
--text-secondary: #666666
--accent: #7c3aed
```

### 4.3 响应式断点

| 断点 | 宽度 | 布局 |
|------|------|------|
| Mobile | < 640px | 单列，播放器在上 |
| Tablet | 640px - 1024px | 双列，播放器+列表 |
| Desktop | > 1024px | 双列，更宽的侧边栏 |

---

## 五、数据库设计

### SQLite Schema

```sql
-- 用户表
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 播放列表
CREATE TABLE playlists (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 播放列表项
CREATE TABLE playlist_items (
    id TEXT PRIMARY KEY,
    playlist_id TEXT NOT NULL,
    media_url TEXT NOT NULL,
    title TEXT NOT NULL,
    thumbnail TEXT,
    source TEXT,
    position INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id)
);

-- 收藏
CREATE TABLE favorites (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    media_url TEXT NOT NULL,
    title TEXT NOT NULL,
    thumbnail TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, media_url)
);

-- 历史
CREATE TABLE history (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    media_url TEXT NOT NULL,
    title TEXT NOT NULL,
    thumbnail TEXT,
    position INTEGER DEFAULT 0,
    duration INTEGER,
    last_played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, media_url)
);

-- 索引
CREATE INDEX idx_playlists_user ON playlists(user_id);
CREATE INDEX idx_favorites_user ON favorites(user_id);
CREATE INDEX idx_history_user ON history(user_id);
CREATE INDEX idx_history_time ON history(last_played_at DESC);
```

---

## 六、API 完整列表

### 认证相关
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录 |
| GET | /api/auth/profile | 获取用户信息 |
| POST | /api/auth/sync | 同步数据 |

### 搜索相关
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/search | 多平台搜索 |
| GET | /api/search/video | 视频搜索 |
| GET | /api/search/music | 音乐搜索 |

### 媒体相关
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/extract | 提取媒体链接 |
| GET | /api/proxy | 代理播放 |
| GET | /api/download | 下载媒体 |
| GET | /api/lyric | 获取歌词 |

### 播放列表
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/playlists | 获取所有列表 |
| POST | /api/playlists | 创建列表 |
| PUT | /api/playlists/:id | 更新列表 |
| DELETE | /api/playlists/:id | 删除列表 |
| POST | /api/playlists/:id/items | 添加项 |
| DELETE | /api/playlists/:id/items/:itemId | 移除项 |

### 收藏与历史
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/favorites | 获取收藏 |
| POST | /api/favorites | 添加收藏 |
| DELETE | /api/favorites/:id | 取消收藏 |
| GET | /api/history | 获取历史 |
| POST | /api/history | 记录历史 |
| DELETE | /api/history | 清空历史 |

---

## 七、文件结构

```
media-player/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── database.py          # 数据库连接
│   ├── models/              # SQLAlchemy 模型
│   │   ├── user.py
│   │   ├── playlist.py
│   │   └── media.py
│   ├── routers/             # API 路由
│   │   ├── auth.py
│   │   ├── search.py
│   │   ├── media.py
│   │   ├── playlist.py
│   │   └── sync.py
│   ├── services/            # 业务逻辑
│   │   ├── extractor.py
│   │   ├── lyric.py
│   │   └── download.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   │   ├── Player/
│   │   │   ├── SearchBar/
│   │   │   ├── PlaylistPanel/
│   │   │   ├── MiniPlayer/
│   │   │   └── LyricPanel/
│   │   ├── hooks/
│   │   │   ├── usePlayer.ts
│   │   │   ├── useAuth.ts
│   │   │   └── useSync.ts
│   │   ├── stores/          # Zustand stores
│   │   │   ├── playerStore.ts
│   │   │   ├── authStore.ts
│   │   │   └── playlistStore.ts
│   │   ├── db/              # IndexedDB
│   │   │   └── database.ts
│   │   └── utils/
│   │       ├── lrc-parser.ts
│   │       └── format.ts
│   ├── public/
│   │   ├── manifest.json
│   │   └── icons/
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   └── plans/
│       └── 2026-03-21-media-player-v2-design.md
└── README.md
```

---

## 八、实现计划

### Phase 1: 基础重构（1-2 天）
- [ ] 初始化 Git 仓库
- [ ] 创建 React + TypeScript 前端框架
- [ ] 重构后端为模块化结构
- [ ] 设置 SQLite 数据库

### Phase 2: 核心功能（2-3 天）
- [ ] 实现播放器组件（Plyr + HLS.js）
- [ ] 实现播放列表管理
- [ ] 实现收藏和历史记录
- [ ] IndexedDB 本地存储

### Phase 3: 账号系统（1 天）
- [ ] 用户注册/登录 API
- [ ] JWT 认证中间件
- [ ] 前端登录页面
- [ ] 数据同步逻辑

### Phase 4: 增强功能（1-2 天）
- [ ] 歌词获取和显示
- [ ] 下载功能
- [ ] Mini 播放器
- [ ] 进度记忆

### Phase 5: PWA 和部署（1 天）
- [ ] manifest.json 和图标
- [ ] Service Worker
- [ ] Dockerfile
- [ ] docker-compose.yml

---

*文档版本：v1.0*  
*最后更新：2026-03-21*