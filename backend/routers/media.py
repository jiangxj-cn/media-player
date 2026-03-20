from fastapi import APIRouter
from ..services.extractor import extract_media_info
from ..schemas.media import MediaInfo
import asyncio

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
    """代理播放（绕过 CORS）"""
    from fastapi.responses import StreamingResponse
    import aiohttp
    
    async def stream():
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                async for chunk in resp.content.iter_chunked(8192):
                    yield chunk
    
    return StreamingResponse(stream(), media_type="video/mp4")
