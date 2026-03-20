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

from .database import engine, Base
from .routers import search, media, auth, playlist

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

# 挂载前端静态文件
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# 注册路由
app.include_router(search.router)
app.include_router(media.router)
app.include_router(auth.router)
app.include_router(playlist.router)

@app.get("/")
async def root():
    """返回前端页面"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Media Player API v2.0", "docs": "/docs"}

@app.get("/api")
async def api_info():
    return {"message": "Media Player API v2.0", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
