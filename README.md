# Media Player

多平台视频音乐播放器 - 支持在线视频搜索、播放、音乐收藏、歌单管理等功能

## 功能列表

- 🎬 **视频搜索与播放** - 支持多个平台的视频搜索和在线播放
- 🎵 **音乐播放** - 支持在线音乐搜索和播放
- 📝 **歌单管理** - 创建、编辑、删除个人歌单
- ❤️ **收藏功能** - 收藏喜欢的视频和音乐
- 📜 **播放历史** - 自动记录播放历史
- 🎤 **歌词显示** - 实时同步歌词显示
- ⬇️ **下载支持** - 支持视频和音乐下载
- 📱 **PWA 支持** - 可安装到桌面，支持离线使用
- 🐳 **Docker 部署** - 一键容器化部署

## 快速开始

### 开发环境

```bash
# 克隆项目
cd media-player

# 启动开发服务器
./start.sh
```

或手动启动：

```bash
# 启动后端
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（新终端）
cd frontend
npm run dev
```

访问 http://localhost:5173 (前端) 或 http://localhost:8000 (后端 API)

### 生产环境 - Docker 部署

#### 方式一：使用 Docker Compose（推荐）

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 方式二：使用 Docker

```bash
# 构建镜像
docker build -t media-player .

# 运行容器
docker run -d \
  --name media-player \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e SECRET_KEY=your-secret-key \
  media-player
```

访问 http://localhost:8000

## Docker 部署说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | 应用密钥（用于 session 等） | `change-me-in-production` |
| `DATABASE_URL` | 数据库连接 URL | `sqlite:////app/data/media_player.db` |

### 数据持久化

数据目录通过 volume 挂载到 `./data`，包含：
- SQLite 数据库文件
- 下载的文件
- 其他持久化数据

### 生产环境建议

1. **修改密钥**：务必修改 `SECRET_KEY` 为随机生成的安全密钥
2. **使用 HTTPS**：生产环境建议配置反向代理（如 Nginx）启用 HTTPS
3. **定期备份**：定期备份 `./data` 目录

## 开发指南

### 项目结构

```
media-player/
├── backend/          # Python FastAPI 后端
│   ├── routers/     # API 路由
│   ├── database.py  # 数据库配置
│   └── main.py      # 应用入口
├── frontend/         # React + TypeScript + Vite 前端
│   ├── src/         # 源代码
│   ├── public/      # 静态资源
│   └── dist/        # 构建产物
├── data/            # 数据目录
├── Dockerfile       # Docker 构建文件
├── docker-compose.yml
└── README.md
```

### 技术栈

**后端**
- Python 3.11
- FastAPI
- SQLite / SQLAlchemy
- Uvicorn

**前端**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router

### 添加新功能

1. **后端 API**：在 `backend/routers/` 创建新路由文件
2. **前端页面**：在 `frontend/src/` 创建新组件
3. **数据库模型**：在 `backend/models.py` 添加新模型

### PWA 开发

Service Worker 位于 `frontend/public/sw.js`，修改后需要：
1. 更新 `CACHE_NAME` 版本号
2. 重新构建前端：`npm run build`

## 许可证

MIT License
