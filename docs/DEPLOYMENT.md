# Media Player 部署指南

## 目录
- [环境要求](#环境要求)
- [开发环境](#开发环境)
- [生产部署](#生产部署)
- [Docker 部署](#docker-部署)
- [Nginx 配置](#nginx-配置)
- [常见问题](#常见问题)

---

## 环境要求

### 后端
- Python 3.11+
- SQLite 3
- FFmpeg (可选，用于媒体转换)

### 前端
- Node.js 18+
- npm 或 pnpm

---

## 开发环境

### 1. 克隆项目

```bash
git clone https://github.com/jiangxj-cn/media-player.git
cd media-player
```

### 2. 后端设置

```bash
# 创建虚拟环境
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r ../requirements.txt

# 启动开发服务器
cd ..
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --app-dir . --reload
```

### 3. 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器会代理 API 请求到 `http://localhost:8000`。

### 4. 运行测试

```bash
# 后端单元测试
cd backend
source .venv/bin/activate
pytest tests -v

# E2E 测试 (需要先启动服务)
cd ..
npm run test:e2e
```

---

## 生产部署

### 1. 构建前端

```bash
cd frontend
npm install
npm run build
```

构建产物会生成到 `static/` 目录。

### 2. 配置环境变量

创建 `.env` 文件：

```env
# 安全配置
SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 数据库
DATABASE_URL=sqlite:///./data/media_player.db

# 日志
LOG_LEVEL=INFO
```

### 3. 使用 Gunicorn (推荐)

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
cd media-player
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 4. 使用 Systemd 服务

创建服务文件 `/etc/systemd/system/media-player.service`：

```ini
[Unit]
Description=Media Player Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/media-player
Environment="PATH=/opt/media-player/backend/.venv/bin"
ExecStart=/opt/media-player/backend/.venv/bin/gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable media-player
sudo systemctl start media-player
```

---

## Docker 部署

### 1. 构建镜像

```bash
docker build -t media-player:latest .
```

### 2. 使用 Docker Compose

```bash
docker-compose up -d
```

`docker-compose.yml` 配置：

```yaml
version: '3.8'
services:
  media-player:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - SECRET_KEY=your-secret-key
    restart: unless-stopped
```

### 3. 运行容器

```bash
docker run -d \
  --name media-player \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e SECRET_KEY=your-secret-key \
  media-player:latest
```

---

## Nginx 配置

### 反向代理配置

创建 `/etc/nginx/sites-available/media-player`：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # HTTPS 重定向
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 证书 (使用 Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 代理到后端
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态文件缓存
    location /static/ {
        proxy_pass http://127.0.0.1:8000/static/;
        proxy_cache_valid 200 7d;
        add_header Cache-Control "public, max-age=604800";
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/media-player /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 监控和日志

### API 监控端点

- `/api/health` - 健康状态检查
- `/api/stats` - API 响应时间统计

### 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('media-player.log'),
        logging.StreamHandler()
    ]
)
```

---

## 常见问题

### Q: 搜索功能不工作？

**A:** 检查网络连接和 yt-dlp 版本：
```bash
pip install --upgrade yt-dlp
```

### Q: 视频无法播放？

**A:** 检查以下几点：
1. 浏览器是否支持 HLS（大部分现代浏览器支持）
2. 是否有 CORS 问题（检查控制台错误）
3. 视频源是否可访问

### Q: 如何更新？

```bash
git pull
cd frontend && npm install && npm run build
cd ../backend && source .venv/bin/activate && pip install -r ../requirements.txt
sudo systemctl restart media-player
```

### Q: 数据库在哪里？

**A:** 默认使用 SQLite，数据库文件位于 `data/media_player.db`。

### Q: 如何备份数据？

```bash
# 备份数据库
cp data/media_player.db data/media_player.db.bak

# 或使用 SQLite 导出
sqlite3 data/media_player.db ".dump" > backup.sql
```

---

## 性能优化建议

1. **启用 Gzip 压缩**：在 Nginx 中启用 gzip
2. **CDN 加速**：静态资源使用 CDN
3. **缓存策略**：设置合适的 Cache-Control 头
4. **负载均衡**：使用 Nginx 负载均衡多个实例
5. **数据库优化**：定期清理历史记录，添加索引

---

## 安全建议

1. **更改默认密钥**：生成安全的 `SECRET_KEY`
2. **启用 HTTPS**：使用 Let's Encrypt 免费证书
3. **限制 CORS**：生产环境设置具体的允许域名
4. **定期更新**：保持依赖项最新
5. **备份数据**：定期备份数据库

---

## 支持

如有问题，请提交 Issue: https://github.com/jiangxj-cn/media-player/issues