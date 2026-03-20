#!/usr/bin/env python3
"""
Web Media Player Backend
基于 yt-dlp 的视频/音乐链接提取服务 + 资源搜索
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import yt_dlp
import asyncio
import aiohttp
import urllib.parse
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

app = FastAPI(title="Media Player API", version="1.0.0")

# 挂载前端静态文件
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=4)


class PlayRequest(BaseModel):
    url: str
    format: Optional[str] = "best"  # best, video, audio


class MediaInfo(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    uploader: Optional[str] = None
    direct_url: Optional[str] = None
    audio_url: Optional[str] = None
    formats: list = []


def extract_media_info(url: str, format_type: str = "best"):
    """提取媒体信息"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            result = {
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'formats': [],
            }
            
            # 获取最佳视频+音频
            if format_type in ['best', 'video']:
                for f in info.get('formats', []):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        if f.get('url'):
                            result['direct_url'] = f['url']
                            break
                
                # 如果没找到合并流，分别获取视频和音频
                if not result.get('direct_url'):
                    video_url = None
                    audio_url = None
                    
                    for f in info.get('formats', []):
                        if f.get('vcodec') != 'none' and f.get('url'):
                            video_url = f['url']
                        if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url'):
                            audio_url = f['url']
                    
                    if video_url:
                        result['direct_url'] = video_url
                    if audio_url:
                        result['audio_url'] = audio_url
            
            # 仅音频
            elif format_type == 'audio':
                for f in info.get('formats', []):
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        if f.get('url'):
                            result['audio_url'] = f['url']
                            break
            
            # 获取可用格式列表
            for f in info.get('formats', [])[:10]:
                if f.get('url'):
                    result['formats'].append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f.get('resolution') or f.get('height'),
                        'filesize': f.get('filesize'),
                        'url': f.get('url'),
                    })
            
            return result
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
async def root():
    """返回前端页面"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Media Player API", "docs": "/docs"}


@app.get("/api")
async def api_info():
    return {"message": "Media Player API", "docs": "/docs"}


@app.post("/api/extract", response_model=MediaInfo)
async def extract(request: PlayRequest):
    """提取媒体链接"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor, 
        extract_media_info, 
        request.url, 
        request.format
    )
    return result


@app.get("/api/extract")
async def extract_get(url: str, format: str = "best"):
    """GET 方式提取"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor, 
        extract_media_info, 
        url, 
        format
    )
    return result


@app.get("/api/proxy")
async def proxy(url: str):
    """代理播放（绕过 CORS）"""
    async def stream():
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                async for chunk in resp.content.iter_chunked(8192):
                    yield chunk
    
    return StreamingResponse(stream(), media_type="video/mp4")


# ==================== 搜索功能 ====================

class SearchResult(BaseModel):
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    uploader: Optional[str] = None
    source: str = "unknown"


async def search_youtube(query: str, max_results: int = 10) -> List[dict]:
    """搜索 YouTube"""
    results = []
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'playlistend': max_results,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_url = f"ytsearch{max_results}:{query}"
            info = ydl.extract_info(search_url, download=False)
            
            for entry in info.get('entries', []):
                results.append({
                    'title': entry.get('title', 'Unknown'),
                    'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'thumbnail': entry.get('thumbnails', [{}])[-1].get('url') if entry.get('thumbnails') else None,
                    'duration': str(entry.get('duration', '')),
                    'uploader': entry.get('uploader', ''),
                    'source': 'youtube'
                })
    except Exception as e:
        print(f"YouTube search error: {e}")
    
    return results


async def search_bilibili(query: str, max_results: int = 10) -> List[dict]:
    """搜索 B站"""
    results = []
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.bilibili.com/x/web-interface/search/type?keyword={urllib.parse.quote(query)}&search_type=video&page_size={max_results}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.bilibili.com'
            }
            
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                
                for item in data.get('data', {}).get('result', []):
                    results.append({
                        'title': item.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                        'url': f"https://www.bilibili.com/video/{item.get('bvid')}",
                        'thumbnail': f"https:{item.get('pic', '')}" if item.get('pic', '').startswith('//') else item.get('pic'),
                        'duration': item.get('duration', ''),
                        'uploader': item.get('author', ''),
                        'source': 'bilibili'
                    })
    except Exception as e:
        print(f"Bilibili search error: {e}")
    
    return results


async def search_netease_music(query: str, max_results: int = 10) -> List[dict]:
    """搜索网易云音乐"""
    results = []
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://music.163.com/api/cloudsearch/pc?s={urllib.parse.quote(query)}&type=1&limit={max_results}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://music.163.com'
            }
            
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                
                for song in data.get('result', {}).get('songs', []):
                    artists = ', '.join([a.get('name', '') for a in song.get('ar', [])])
                    results.append({
                        'title': f"{song.get('name', '')} - {artists}",
                        'url': f"https://music.163.com/#/song?id={song.get('id')}",
                        'thumbnail': song.get('al', {}).get('picUrl', ''),
                        'duration': f"{song.get('dt', 0) // 60000}:{(song.get('dt', 0) % 60000) // 1000:02d}",
                        'uploader': artists,
                        'source': 'netease'
                    })
    except Exception as e:
        print(f"Netease search error: {e}")
    
    return results


@app.get("/api/search")
async def search(q: str, source: str = "all", max_results: int = 10):
    """
    搜索资源
    
    - q: 搜索关键词
    - source: youtube / bilibili / netease / all
    - max_results: 每个源的最大结果数
    """
    all_results = []
    
    tasks = []
    if source in ['all', 'youtube']:
        tasks.append(('youtube', search_youtube(q, max_results)))
    if source in ['all', 'bilibili']:
        tasks.append(('bilibili', search_bilibili(q, max_results)))
    if source in ['all', 'netease']:
        tasks.append(('netease', search_netease_music(q, max_results)))
    
    for name, task in tasks:
        try:
            results = await task
            all_results.extend(results)
        except Exception as e:
            print(f"{name} search failed: {e}")
    
    return {
        'query': q,
        'total': len(all_results),
        'results': all_results
    }


@app.get("/api/search/video")
async def search_video(q: str, max_results: int = 10):
    """搜索视频 (YouTube + B站)"""
    youtube_results = await search_youtube(q, max_results)
    bilibili_results = await search_bilibili(q, max_results)
    
    return {
        'query': q,
        'total': len(youtube_results) + len(bilibili_results),
        'results': youtube_results + bilibili_results
    }


@app.get("/api/search/music")
async def search_music(q: str, max_results: int = 10):
    """搜索音乐 (网易云)"""
    results = await search_netease_music(q, max_results)
    
    return {
        'query': q,
        'total': len(results),
        'results': results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)