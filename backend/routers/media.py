from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..services.extractor import extract_media_info
from ..schemas.media import MediaInfo
import asyncio
import aiohttp

router = APIRouter(prefix="/api", tags=["media"])

@router.post("/extract", response_model=MediaInfo)
async def extract(url: str, format: str = "best"):
    """提取媒体链接"""
    loop = asyncio.get_event_loop()
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor(max_workers=4)
    result = await loop.run_in_executor(
        executor, 
        extract_media_info, 
        url, 
        format
    )
    return result

@router.get("/extract", response_model=MediaInfo)
async def extract_get(url: str, format: str = "best"):
    """GET 方式提取"""
    loop = asyncio.get_event_loop()
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor(max_workers=4)
    result = await loop.run_in_executor(
        executor, 
        extract_media_info, 
        url, 
        format
    )
    return result

@router.get("/proxy")
async def proxy(url: str):
    """代理播放（绕过 CORS 和 403）- 优化版"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.bilibili.com/',
    }
    
    # 设置超时和连接池
    timeout = aiohttp.ClientTimeout(total=300, connect=10)
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
    
    async def stream():
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.get(url, headers=headers) as resp:
                # 使用更大的 chunk 提高传输效率
                async for chunk in resp.content.iter_chunked(65536):  # 64KB chunks
                    yield chunk
    
    return StreamingResponse(stream(), media_type="video/mp4")
