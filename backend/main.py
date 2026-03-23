#!/usr/bin/env python3
"""
Web Media Player Backend - v2.0
模块化架构
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os

from .database import engine, Base
from .routers import search, media, auth, playlist, favorites, history, lyric, download
from .middleware import TimingMiddleware, get_api_stats, get_health_status

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Media Player API", version="2.0.0")

# 添加响应时间监控中间件
app.add_middleware(TimingMiddleware)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由（必须在静态文件挂载之前）
app.include_router(search.router)
app.include_router(media.router)
app.include_router(auth.router)
app.include_router(playlist.router)
app.include_router(favorites.router)
app.include_router(history.router)
app.include_router(lyric.router)
app.include_router(download.router)

@app.get("/api")
async def api_info():
    return {"message": "Media Player API v2.0", "docs": "/docs"}

@app.get("/api/stats")
async def api_stats():
    """获取 API 统计信息"""
    return get_api_stats()

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return get_health_status()

# 挂载静态文件（必须在所有 API 路由之后）
STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.exists():
    # 生产环境：服务构建后的前端文件
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
