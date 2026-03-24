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
        'socket_timeout': 10,
        'retries': 2,
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
            # 完整的请求头，模拟浏览器行为
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.bilibili.com',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Origin': 'https://www.bilibili.com',
                'Connection': 'keep-alive',
                # buvid3 是 B站的反爬参数，使用随机生成的值
                'Cookie': 'buvid3=' + _generate_buvid()
            }
            
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 412:
                    print("Bilibili API returned 412, falling back to yt-dlp")
                    return await _search_bilibili_fallback(query, max_results)
                
                data = await resp.json()
                
                if data.get('code') != 0:
                    print(f"Bilibili API error: {data.get('message')}")
                    return await _search_bilibili_fallback(query, max_results)
                
                for item in data.get('data', {}).get('result', []):
                    # 处理缩略图 URL，使用代理绕过防盗链
                    pic_url = f"https:{item.get('pic', '')}" if item.get('pic', '').startswith('//') else item.get('pic')
                    # 使用服务器代理绕过防盗链（支持所有B站图片域名）
                    if pic_url and ('hdslb.com' in pic_url or 'bilibili.com' in pic_url or 'biliimg.com' in pic_url):
                        pic_url = f"/api/image?url={urllib.parse.quote(pic_url)}"
                    
                    results.append({
                        'id': item.get('bvid'),
                        'title': item.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                        'url': f"https://www.bilibili.com/video/{item.get('bvid')}",
                        'thumbnail': pic_url,
                        'duration': item.get('duration', ''),
                        'uploader': item.get('author', ''),
                        'source': 'bilibili'
                    })
    except Exception as e:
        print(f"Bilibili search error: {e}, falling back to yt-dlp")
        return await _search_bilibili_fallback(query, max_results)
    
    # 设置缓存
    _set_cache(cache_key, results)
    return results


def _generate_buvid() -> str:
    """生成 B站 buvid3 参数"""
    import uuid
    return f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}"


async def _search_bilibili_fallback(query: str, max_results: int = 10) -> List[Dict]:
    """使用 yt-dlp 作为 B站搜索的备选方案"""
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
            search_url = f"bvsearch{max_results}:{query}"
            info = ydl.extract_info(search_url, download=False)
            
            for entry in info.get('entries', []):
                results.append({
                    'id': entry.get('id'),
                    'title': entry.get('title', 'Unknown'),
                    'url': f"https://www.bilibili.com/video/{entry.get('id')}",
                    'thumbnail': entry.get('thumbnails', [{}])[-1].get('url') if entry.get('thumbnails') else None,
                    'duration': str(entry.get('duration', '')),
                    'uploader': entry.get('uploader', ''),
                    'source': 'bilibili'
                })
    except Exception as e:
        print(f"Bilibili fallback error: {e}")
    
    return results


async def search_netease_music(query: str, max_results: int = 10):
    """搜索网易云音乐 (使用 yt-dlp 作为备选)"""
    # 检查缓存
    cache_key = _get_cache_key(query, 'netease', max_results)
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached
    
    results = []
    
    # 尝试使用网易云音乐公开 API
    try:
        results = await _search_netease_api(query, max_results)
        if results:
            _set_cache(cache_key, results)
            return results
    except Exception as e:
        print(f"Netease API failed: {e}, falling back to yt-dlp")
    
    # 备选方案：使用 yt-dlp 搜索 YouTube Music
    try:
        results = await _search_youtube_music(query, max_results)
    except Exception as e:
        print(f"Netease fallback error: {e}")
    
    _set_cache(cache_key, results)
    return results


async def _search_netease_api(query: str, max_results: int = 10) -> List[Dict]:
    """使用网易云音乐公开 API 搜索"""
    results = []
    
    try:
        async with aiohttp.ClientSession() as session:
            # 使用推荐搜索 API（不需要加密）
            url = f"https://music.163.com/api/search/suggest/keywords?limit={max_results}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://music.163.com',
                'Accept': 'application/json',
            }
            
            # 使用 POST 请求
            data = aiohttp.FormData()
            data.add_field('s', query)
            
            async with session.post(url, headers=headers, data=data, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                json_data = await resp.json()
                
                if json_data.get('code') == 200:
                    # 从建议结果中提取
                    keywords = json_data.get('result', {}).get('keywords', [])
                    for kw in keywords[:max_results]:
                        results.append({
                            'id': str(hash(kw.get('keyword', ''))),
                            'title': kw.get('keyword', ''),
                            'url': f"https://music.163.com/#/search/m/?s={kw.get('keyword', '')}",
                            'thumbnail': '',
                            'duration': '',
                            'uploader': '',
                            'source': 'netease'
                        })
                    
                    if results:
                        return results
                
                # 如果建议 API 不工作，尝试其他方法
                raise Exception("Suggest API not returning songs")
    except Exception as e:
        raise e
    
    return results


async def _search_youtube_music(query: str, max_results: int = 10) -> List[Dict]:
    """使用 yt-dlp 搜索 YouTube Music 作为备选"""
    results = []
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'playlistend': max_results,
        'socket_timeout': 10,
        'retries': 2,
    }
    
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 使用 yt-dlp 搜索 YouTube Music
            search_url = f"ytsearch{max_results}:{query} music"
            info = ydl.extract_info(search_url, download=False)
            
            for entry in info.get('entries', []):
                results.append({
                    'id': entry.get('id'),
                    'title': entry.get('title', 'Unknown'),
                    'url': f"https://music.youtube.com/watch?v={entry.get('id')}",
                    'thumbnail': entry.get('thumbnails', [{}])[-1].get('url') if entry.get('thumbnails') else None,
                    'duration': str(entry.get('duration', '')),
                    'uploader': entry.get('uploader', ''),
                    'source': 'netease'  # 保持 netease 作为源，因为这是备选方案
                })
    except Exception as e:
        print(f"YouTube Music fallback error: {e}")
    
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