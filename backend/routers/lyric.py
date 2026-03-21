from fastapi import APIRouter, HTTPException
from ..schemas.lyric import LyricRequest, LyricResponse
import re
import json

router = APIRouter(prefix="/api/lyric", tags=["lyric"])

async def fetch_netease_lyric(song_id: str) -> str:
    """从网易云音乐获取歌词"""
    import aiohttp
    
    url = f"http://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={
            "Referer": "http://music.163.com/",
            "User-Agent": "Mozilla/5.0"
        }) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=404, detail="Lyric not found")
            
            data = await resp.json()
            
            if "lrc" in data and "lyric" in data["lrc"]:
                return data["lrc"]["lyric"]
            
            raise HTTPException(status_code=404, detail="Lyric not found")

async def fetch_qq_lyric(song_id: str) -> str:
    """从 QQ 音乐获取歌词"""
    import aiohttp
    
    url = f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?songmid={song_id}&g_tk=5381&format=json&inCharset=utf-8&outCharset=utf-8"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={
            "Referer": "https://y.qq.com/",
            "User-Agent": "Mozilla/5.0"
        }) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=404, detail="Lyric not found")
            
            text = await resp.text()
            # QQ 音乐返回的是 JSONP，需要去掉回调函数
            match = re.search(r'\((.*)\)', text)
            if match:
                data = json.loads(match.group(1))
                if "lyric" in data:
                    import base64
                    return base64.b64decode(data["lyric"]).decode("utf-8")
            
            raise HTTPException(status_code=404, detail="Lyric not found")

def extract_song_id(url: str, source: str) -> str:
    """从 URL 提取歌曲 ID"""
    if source == "netease":
        # 网易云：https://music.163.com/song?id=123456
        match = re.search(r'[?&]id=(\d+)', url)
        if match:
            return match.group(1)
        # 或者 https://music.163.com/#/song?id=123456
        match = re.search(r'song/(\d+)', url)
        if match:
            return match.group(1)
    elif source == "qq":
        # QQ 音乐：https://y.qq.com/portal/songmid/XXX.html
        match = re.search(r'songmid/([A-Za-z0-9]+)', url)
        if match:
            return match.group(1)
        # 或者 https://y.qq.com/n/ryqq/songDetail/XXX
        match = re.search(r'songDetail/([A-Za-z0-9]+)', url)
        if match:
            return match.group(1)
    
    raise HTTPException(status_code=400, detail="Invalid URL format")

@router.get("/", response_model=LyricResponse)
async def get_lyric(url: str, source: str = "netease"):
    """
    获取歌词
    - url: 歌曲 URL
    - source: 来源 (netease, qq)
    - 返回 LRC 格式歌词
    """
    try:
        song_id = extract_song_id(url, source)
        
        if source == "netease":
            lrc = await fetch_netease_lyric(song_id)
        elif source == "qq":
            lrc = await fetch_qq_lyric(song_id)
        else:
            raise HTTPException(status_code=400, detail="Unsupported source")
        
        return {
            "url": url,
            "source": source,
            "lrc": lrc
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lyric: {str(e)}")
