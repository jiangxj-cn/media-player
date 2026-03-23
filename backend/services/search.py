"""
搜索服务模块
支持 YouTube、B站、网易云音乐搜索
带有内存缓存优化
"""

import aiohttp
import urllib.parse
import time
from functools import lru_cache
from typing import Dict, List, Optional, Any
import hashlib

# 内存缓存配置
CACHE_TTL = 300  # 缓存有效期 5 分钟
_search_cache: Dict[str, Dict[str, Any]] = {}


def _get_cache_key(query: str, source: str, max_results: int) -> str:
    """生成缓存键"""
    key_str = f"{source}:{query}:{max_results}"
    return hashlib.md5(key_str.encode()).hexdigest()


def _get_from_cache(key: str) -> Optional[List[Dict]]:
    """从缓存获取结果"""
    if key in _search_cache:
        cached = _search_cache[key]
        if time.time() - cached['timestamp'] < CACHE_TTL:
            return cached['data']
        else:
            del _search_cache[key]
    return None


def _set_cache(key: str, data: List[Dict]) -> None:
    """设置缓存"""
    # 限制缓存大小，最多保留 100 个缓存项
    if len(_search_cache) >= 100:
        # 删除最旧的缓存
        oldest_key = min(_search_cache.keys(), key=lambda k: _search_cache[k]['timestamp'])
        del _search_cache[oldest_key]
    
    _search_cache[key] = {
        'data': data,
        'timestamp': time.time()
    }


async def search_youtube(query: str, max_results: int = 10):
    """搜索 YouTube"""
    # 检查缓存
    cache_key = _get_cache_key(query, 'youtube', max_results)
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached
    
    results = []
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'playlistend': max_results,
    }
    
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_url = f"ytsearch{max_results}:{query}"
            info = ydl.extract_info(search_url, download=False)
            
            for entry in info.get('entries', []):
                results.append({
                    'id': entry.get('id'),
                    'title': entry.get('title', 'Unknown'),
                    'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'thumbnail': entry.get('thumbnails', [{}])[-1].get('url') if entry.get('thumbnails') else None,
                    'duration': str(entry.get('duration', '')),
                    'uploader': entry.get('uploader', ''),
                    'source': 'youtube'
                })
    except Exception as e:
        print(f"YouTube search error: {e}")
    
    # 设置缓存
    _set_cache(cache_key, results)
    return results


async def search_bilibili(query: str, max_results: int = 10):
    """搜索 B 站"""
    # 检查缓存
    cache_key = _get_cache_key(query, 'bilibili', max_results)
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached
    
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
                        'id': item.get('bvid'),
                        'title': item.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                        'url': f"https://www.bilibili.com/video/{item.get('bvid')}",
                        'thumbnail': f"https:{item.get('pic', '')}" if item.get('pic', '').startswith('//') else item.get('pic'),
                        'duration': item.get('duration', ''),
                        'uploader': item.get('author', ''),
                        'source': 'bilibili'
                    })
    except Exception as e:
        print(f"Bilibili search error: {e}")
    
    # 设置缓存
    _set_cache(cache_key, results)
    return results


async def search_netease_music(query: str, max_results: int = 10):
    """搜索网易云音乐"""
    # 检查缓存
    cache_key = _get_cache_key(query, 'netease', max_results)
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached
    
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
                        'id': str(song.get('id')),
                        'title': f"{song.get('name', '')} - {artists}",
                        'url': f"https://music.163.com/#/song?id={song.get('id')}",
                        'thumbnail': song.get('al', {}).get('picUrl', ''),
                        'duration': f"{song.get('dt', 0) // 60000}:{(song.get('dt', 0) % 60000) // 1000:02d}",
                        'uploader': artists,
                        'source': 'netease'
                    })
    except Exception as e:
        print(f"Netease search error: {e}")
    
    # 设置缓存
    _set_cache(cache_key, results)
    return results


def clear_cache():
    """清空缓存"""
    global _search_cache
    _search_cache = {}


def get_cache_stats():
    """获取缓存统计"""
    return {
        'total_items': len(_search_cache),
        'items': [
            {
                'key': k,
                'age_seconds': int(time.time() - v['timestamp']),
                'result_count': len(v['data'])
            }
            for k, v in _search_cache.items()
        ]
    }