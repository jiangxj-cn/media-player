from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from ..services.extractor import (
    extract_media_info, 
    extract_media_info_async,
    extract_formats_async,
    get_supported_sources
)
from ..schemas.media import MediaInfo
import asyncio
import aiohttp
import logging
from typing import Optional

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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'identity',  # 禁用压缩以支持 Range
        'Referer': 'https://www.bilibili.com/',
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