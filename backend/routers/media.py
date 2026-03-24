from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from ..services.extractor import (
    extract_media_info, 
    extract_media_info_async,
    extract_formats_async,
    get_supported_sources,
    extract_youtube_video_id
)
from ..schemas.media import MediaInfo
import asyncio
import aiohttp
import logging
from typing import Optional
import subprocess
import re
import httpx
from functools import lru_cache

router = APIRouter(prefix="/api", tags=["media"])
logger = logging.getLogger(__name__)


@router.post("/extract", response_model=MediaInfo)
async def extract(url: str, format: str = Query("best", description="视频质量: best/medium/low/audio")):
    """提取媒体链接
    
    支持的质量选项:
    - best: 最高质量（默认）
    - medium: 中等质量 (720p以下)
    - low: 低质量 (480p以下)
    - audio: 仅音频
    """
    try:
        result = await extract_media_info_async(url, format)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extract failed for {url}: {e}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)[:100]}")


@router.get("/extract", response_model=MediaInfo)
async def extract_get(url: str, format: str = Query("best", description="视频质量: best/medium/low/audio")):
    """GET 方式提取媒体链接"""
    try:
        result = await extract_media_info_async(url, format)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extract failed for {url}: {e}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)[:100]}")


@router.get("/formats")
async def get_formats(url: str):
    """获取视频可用格式列表（用于质量选择）"""
    try:
        formats = await extract_formats_async(url)
        return {
            "url": url,
            "formats": formats,
            "count": len(formats)
        }
    except Exception as e:
        logger.error(f"Get formats failed for {url}: {e}")
        raise HTTPException(status_code=500, detail=f"获取格式失败: {str(e)[:100]}")


@router.get("/sources")
async def list_sources():
    """获取支持的视频源列表"""
    return {
        "sources": get_supported_sources(),
        "total": len(get_supported_sources())
    }


@router.get("/proxy")
async def proxy(
    url: str, 
    range: Optional[str] = Query(None, description="Range header for partial content")
):
    """代理播放（绕过 CORS 和 403）- 优化版
    
    支持 Range 请求，用于视频拖动
    """
    # 根据 URL 判断来源，设置不同的 Referer
    referer = 'https://www.bilibili.com/'
    if 'youtube' in url.lower() or 'ytimg' in url.lower():
        referer = 'https://www.youtube.com/'
    elif 'douyin' in url.lower():
        referer = 'https://www.douyin.com/'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'identity',  # 禁用压缩以支持 Range
        'Referer': referer,
        'Connection': 'keep-alive',
    }
    
    # 传递 Range header
    if range:
        headers['Range'] = f'bytes={range}'
    
    # 设置超时和连接池
    timeout = aiohttp.ClientTimeout(total=600, connect=30, sock_connect=30, sock_read=60)
    connector = aiohttp.TCPConnector(limit=20, limit_per_host=10, ttl_dns_cache=300)
    
    async def stream():
        try:
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(url, headers=headers) as resp:
                    # 检查响应状态
                    if resp.status not in [200, 206, 302]:
                        logger.error(f"Proxy error: status {resp.status}")
                        raise HTTPException(status_code=resp.status, detail="无法获取视频流")
                    
                    # 获取内容类型
                    content_type = resp.headers.get('Content-Type', 'video/mp4')
                    
                    # 使用更大的 chunk 提高传输效率
                    async for chunk in resp.content.iter_chunked(131072):  # 128KB chunks
                        yield chunk
        except aiohttp.ClientError as e:
            logger.error(f"Proxy streaming error: {e}")
            raise HTTPException(status_code=502, detail=f"代理错误: {str(e)}")
    
    return StreamingResponse(
        stream(), 
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",
        }
    )


@router.get("/proxy/hls")
async def proxy_hls(url: str):
    """HLS (m3u8) 代理 - 用于流媒体播放"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Referer': 'https://www.bilibili.com/',
    }
    
    timeout = aiohttp.ClientTimeout(total=600, connect=30)
    connector = aiohttp.TCPConnector(limit=20, limit_per_host=10)
    
    async def fetch():
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.get(url, headers=headers) as resp:
                content = await resp.text()
                # 重写 m3u8 中的相对路径为代理路径
                lines = content.split('\n')
                rewritten = []
                for line in lines:
                    if line and not line.startswith('#'):
                        # 将相对路径转换为绝对路径
                        if not line.startswith('http'):
                            from urllib.parse import urljoin
                            line = urljoin(url, line)
                        rewritten.append(line)
                    else:
                        rewritten.append(line)
                return '\n'.join(rewritten)
    
    try:
        content = await fetch()
        return StreamingResponse(
            iter([content.encode()]),
            media_type="application/vnd.apple.mpegurl",
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        logger.error(f"HLS proxy error: {e}")
        raise HTTPException(status_code=502, detail=f"HLS代理错误: {str(e)}")


# ==================== YouTube 代理播放 ====================

# 缓存 YouTube 视频 URL (避免频繁调用 yt-dlp)
_youtube_cache: dict = {}

def get_youtube_stream_url(video_id: str, quality: str = "best") -> dict:
    """使用 yt-dlp 获取 YouTube 视频流 URL
    
    Args:
        video_id: YouTube 视频 ID
        quality: 视频质量 (best/medium/low)
    
    Returns:
        dict: 包含视频 URL、标题、缩略图等信息
    """
    import time
    
    # 检查缓存 (缓存 1 小时)
    cache_key = f"{video_id}:{quality}"
    if cache_key in _youtube_cache:
        cached = _youtube_cache[cache_key]
        if time.time() - cached['timestamp'] < 3600:
            logger.info(f"YouTube cache hit: {video_id}")
            return cached
    
    # yt-dlp 格式选择
    if quality == "low":
        format_spec = "worst[ext=mp4]/worst"
    elif quality == "medium":
        format_spec = "best[height<=720][ext=mp4]/best[height<=720]/best"
    else:
        format_spec = "best[ext=mp4]/best"
    
    # 使用 yt-dlp 获取视频 URL
    cmd = [
        "yt-dlp",
        "--no-warnings",
        "--no-playlist",
        "--format", format_spec,
        "--get-url",
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env={**subprocess.os.environ, "YTDL_NO_UPDATE": "1"}
        )
        
        if result.returncode != 0:
            logger.error(f"yt-dlp error: {result.stderr}")
            raise HTTPException(status_code=500, detail=f"视频解析失败: {result.stderr[:100]}")
        
        stream_url = result.stdout.strip()
        
        if not stream_url:
            raise HTTPException(status_code=500, detail="无法获取视频流地址")
        
        # 清理 URL（移除可能的换行符）
        stream_url = stream_url.split('\n')[0].strip()
        
        result_data = {
            'video_id': video_id,
            'title': f"YouTube 视频 ({video_id})",
            'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            'duration': 0,
            'stream_url': stream_url,
            'timestamp': time.time()
        }
        
        # 缓存结果
        _youtube_cache[cache_key] = result_data
        
        return result_data
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="视频解析超时，请稍后重试")
    except Exception as e:
        logger.error(f"YouTube proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"代理错误: {str(e)[:100]}")


@router.get("/youtube/{video_id}")
async def youtube_info(
    video_id: str, 
    quality: str = Query("best", description="视频质量: best/medium/low")
):
    """获取 YouTube 视频信息（通过服务器代理获取）
    
    返回可直接播放的视频流 URL 和视频元信息
    """
    # 验证 video_id 格式
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        raise HTTPException(status_code=400, detail="无效的 YouTube 视频 ID")
    
    try:
        info = get_youtube_stream_url(video_id, quality)
        return {
            "success": True,
            "video_id": video_id,
            "title": info['title'],
            "thumbnail": info['thumbnail'],
            "duration": info['duration'],
            "stream_url": f"/api/youtube/{video_id}/stream?quality={quality}",
            "source": "youtube"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get YouTube info: {e}")
        raise HTTPException(status_code=500, detail=f"获取视频信息失败: {str(e)[:100]}")


@router.get("/youtube/{video_id}/stream")
async def youtube_stream(
    video_id: str,
    quality: str = Query("best", description="视频质量: best/medium/low"),
    request: Request = None
):
    """YouTube 视频流代理
    
    通过服务器代理 YouTube 视频流，支持 Range 请求（视频拖动）
    """
    # 验证 video_id 格式
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        raise HTTPException(status_code=400, detail="无效的 YouTube 视频 ID")
    
    # 获取视频流 URL
    info = get_youtube_stream_url(video_id, quality)
    stream_url = info['stream_url']
    
    # 准备请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'identity',
        'Connection': 'keep-alive',
    }
    
    # 传递 Range header 以支持视频拖动
    range_header = request.headers.get('range') if request else None
    if range_header:
        headers['Range'] = range_header
    
    timeout = httpx.Timeout(600, connect=30, read=60)
    
    async def stream():
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            async with client.stream('GET', stream_url, headers=headers) as response:
                # 检查响应状态
                if response.status_code not in [200, 206]:
                    logger.error(f"YouTube stream error: status {response.status_code}")
                    raise HTTPException(status_code=response.status_code, detail="无法获取视频流")
                
                # 获取内容类型
                content_type = response.headers.get('content-type', 'video/mp4')
                content_length = response.headers.get('content-length')
                content_range = response.headers.get('content-range')
                
                # 传输响应头
                resp_headers = {
                    "Accept-Ranges": "bytes",
                    "Cache-Control": "public, max-age=3600",
                    "Content-Type": content_type,
                }
                
                if content_length:
                    resp_headers["Content-Length"] = content_length
                if content_range:
                    resp_headers["Content-Range"] = content_range
                
                async for chunk in response.aiter_bytes(131072):  # 128KB chunks
                    yield chunk
    
    return StreamingResponse(
        stream(),
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",
        }
    )


@router.get("/youtube/{video_id}/thumbnail")
async def youtube_thumbnail(video_id: str):
    """代理 YouTube 视频缩略图"""
    # 验证 video_id 格式
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        raise HTTPException(status_code=400, detail="无效的 YouTube 视频 ID")
    
    # 使用 YouTube 官方缩略图
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    
    timeout = httpx.Timeout(30, connect=10)
    
    async def fetch():
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(thumbnail_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            return response.content
    
    try:
        content = await fetch()
        return StreamingResponse(
            iter([content]),
            media_type="image/jpeg",
            headers={"Cache-Control": "public, max-age=86400"}  # 缓存 1 天
        )
    except Exception as e:
        logger.error(f"Thumbnail proxy error: {e}")
        raise HTTPException(status_code=502, detail=f"缩略图获取失败: {str(e)[:50]}")


@router.get("/image")
async def proxy_image(url: str):
    """代理图片请求（绕过防盗链）
    
    用于代理 B站、抖音等平台的图片，解决 403 Forbidden 问题
    """
    # 根据 URL 判断来源
    referer = 'https://www.bilibili.com/'
    url_lower = url.lower()
    if 'hdslb.com' in url_lower or 'bilibili.com' in url_lower or 'biliimg.com' in url_lower:
        referer = 'https://www.bilibili.com/'
    elif 'youtube' in url_lower or 'ytimg' in url_lower:
        referer = 'https://www.youtube.com/'
    elif 'douyin' in url_lower:
        referer = 'https://www.douyin.com/'
    elif 'ixigua' in url_lower:
        referer = 'https://www.ixigua.com/'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': referer,
    }
    
    timeout = httpx.Timeout(30, connect=10)
    
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="图片获取失败")
            
            # 获取内容类型
            content_type = response.headers.get('Content-Type', 'image/jpeg')
            
            return StreamingResponse(
                iter([response.content]),
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",  # 缓存 1 天
                    "Access-Control-Allow-Origin": "*"
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image proxy error: {e}")
        raise HTTPException(status_code=502, detail=f"图片代理失败: {str(e)[:50]}")