# Media Player API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api`
- **认证方式**: Bearer Token (JWT)

## 认证 API

### 注册用户

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应**: 
```json
{
  "id": 1,
  "username": "string",
  "email": "string"
}
```

### 登录

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 获取当前用户

```http
GET /api/auth/me
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": 1,
  "username": "string",
  "email": "string"
}
```

---

## 搜索 API

### 综合搜索

```http
GET /api/search?q={query}&source={source}&max_results={limit}
```

**参数**:
- `q` (必需): 搜索关键词
- `source` (可选): `youtube` | `bilibili` | `netease` | `all` (默认: `all`)
- `max_results` (可选): 每个源的最大结果数 (默认: 10)

**响应**:
```json
{
  "query": "string",
  "total": 30,
  "results": [
    {
      "id": "string",
      "title": "string",
      "url": "string",
      "thumbnail": "string",
      "duration": "string",
      "uploader": "string",
      "source": "youtube"
    }
  ]
}
```

### 搜索视频

```http
GET /api/search/video?q={query}&max_results={limit}
```

搜索 YouTube 和 B 站视频。

### 搜索音乐

```http
GET /api/search/music?q={query}&max_results={limit}
```

搜索网易云音乐。

---

## 媒体 API

### 获取媒体信息

```http
GET /api/media?url={url}
```

**参数**:
- `url` (必需): 媒体 URL

**响应**:
```json
{
  "title": "string",
  "url": "string",
  "thumbnail": "string",
  "duration": 3600,
  "formats": [
    {
      "format_id": "string",
      "ext": "mp4",
      "quality": 720,
      "url": "string"
    }
  ],
  "hls_url": "string"
}
```

---

## 播放列表 API

> 需要认证

### 获取播放列表

```http
GET /api/playlist
Authorization: Bearer <token>
```

### 创建播放列表

```http
POST /api/playlist
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Playlist",
  "description": "Description"
}
```

### 更新播放列表

```http
PUT /api/playlist/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

### 删除播放列表

```http
DELETE /api/playlist/{id}
Authorization: Bearer <token>
```

---

## 收藏 API

> 需要认证

### 获取收藏列表

```http
GET /api/favorites
Authorization: Bearer <token>
```

### 添加收藏

```http
POST /api/favorites
Authorization: Bearer <token>
Content-Type: application/json

{
  "media_id": "string",
  "title": "string",
  "url": "string",
  "thumbnail": "string",
  "source": "youtube"
}
```

### 移除收藏

```http
DELETE /api/favorites/{media_id}
Authorization: Bearer <token>
```

---

## 历史记录 API

> 需要认证

### 获取历史记录

```http
GET /api/history
Authorization: Bearer <token>
```

### 添加历史记录

```http
POST /api/history
Authorization: Bearer <token>
Content-Type: application/json

{
  "media_id": "string",
  "title": "string",
  "url": "string",
  "position": 30
}
```

### 清空历史记录

```http
DELETE /api/history
Authorization: Bearer <token>
```

---

## 歌词 API

### 获取歌词

```http
GET /api/lyric?url={url}
```

**响应**:
```json
{
  "lyrics": [
    {
      "time": 0,
      "text": "歌词文本"
    }
  ]
}
```

---

## 下载 API

### 获取下载链接

```http
GET /api/download?url={url}&format={format}
```

**参数**:
- `url` (必需): 媒体 URL
- `format` (可选): 格式 (默认: `best`)

**响应**:
```json
{
  "download_url": "string",
  "filename": "string",
  "size": 12345678
}
```

---

## 错误响应

所有 API 在出错时返回统一格式:

```json
{
  "detail": "错误描述"
}
```

常见 HTTP 状态码:
- `400` - 请求参数错误
- `401` - 未认证
- `403` - 无权限
- `404` - 资源不存在
- `500` - 服务器错误

---

## 开发说明

### 启动开发服务器

```bash
cd /home/admin/media-player
cd backend && source .venv/bin/activate
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --app-dir .. --reload
```

### 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc