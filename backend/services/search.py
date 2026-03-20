import aiohttp
import urllib.parse

async def search_youtube(query: str, max_results: int = 10):
    """搜索 YouTube"""
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


async def search_bilibili(query: str, max_results: int = 10):
    """搜索 B 站"""
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


async def search_netease_music(query: str, max_results: int = 10):
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
