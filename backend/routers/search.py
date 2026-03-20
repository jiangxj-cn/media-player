from fastapi import APIRouter
from ..services.search import search_youtube, search_bilibili, search_netease_music
from ..schemas.media import SearchResponse

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("", response_model=SearchResponse)
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

@router.get("/video")
async def search_video(q: str, max_results: int = 10):
    """搜索视频 (YouTube + B 站)"""
    youtube_results = await search_youtube(q, max_results)
    bilibili_results = await search_bilibili(q, max_results)
    
    return {
        'query': q,
        'total': len(youtube_results) + len(bilibili_results),
        'results': youtube_results + bilibili_results
    }

@router.get("/music")
async def search_music(q: str, max_results: int = 10):
    """搜索音乐 (网易云)"""
    results = await search_netease_music(q, max_results)
    
    return {
        'query': q,
        'total': len(results),
        'results': results
    }
