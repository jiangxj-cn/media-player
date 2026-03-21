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

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Media Player API", version="2.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（生产环境）
# 优先使用构建后的 static 目录（Docker 部署），否则使用 frontend 目录（开发环境）
STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.exists():
    # 生产环境：服务构建后的前端文件
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
else:
    # 开发环境：服务前端源码
    FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
    if FRONTEND_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# 注册路由
app.include_router(search.router)
app.include_router(media.router)
app.include_router(auth.router)
app.include_router(playlist.router)
app.include_router(favorites.router)
app.include_router(history.router)
app.include_router(lyric.router)
app.include_router(download.router)

@app.get("/")
async def root():
    """返回前端页面"""
    # 生产环境：从 static 目录服务
    static_index = Path(__file__).parent.parent / "static" / "index.html"
    if static_index.exists():
        return FileResponse(static_index)
    # 开发环境：从 frontend 目录服务
    frontend_index = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_index.exists():
        return FileResponse(frontend_index)
    return {"message": "Media Player API v2.0", "docs": "/docs"}

@app.get("/api")
async def api_info():
    return {"message": "Media Player API v2.0", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
