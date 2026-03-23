from fastapi import HTTPException
import requests
import re
from urllib.parse import quote

def extract_media_info(url: str, format_type: str = "best"):
    """提取媒体信息 - 使用第三方解析服务"""
    
    if 'bilibili.com' in url or 'b23.tv' in url:
        return extract_bilibili(url)
    elif 'youtube.com' in url or 'youtu.be' in url:
        return extract_youtube(url)
    else:
        raise HTTPException(status_code=400, detail="不支持的视频源")

def extract_bilibili(url: str):
    """B站视频解析 - 使用第三方 API"""
    
    # 米人API - 免费，稳定
    api_url = f"https://api.mir6.com/api/bzjiexi?url={quote(url)}&type=json"
    
    try:
        response = requests.get(api_url, timeout=30)
        data = response.json()
        
        if data.get('code') != 200:
            raise Exception(data.get('msg', '解析失败'))
        
        video_data = data.get('data', [{}])[0]
        
        return {
            'title': data.get('title', 'Unknown'),
            'thumbnail': data.get('imgurl', ''),
            'duration': video_data.get('duration', 0),
            'uploader': data.get('user', {}).get('name', ''),
            'direct_url': video_data.get('video_url', ''),
            'source': 'bilibili',
            'original_url': url,
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"解析服务不可用: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def extract_youtube(url: str):
    """YouTube 视频解析 - 使用第三方 API"""
    
    # 提取视频 ID
    video_id = None
    patterns = [
        r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'embed/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break
    
    if not video_id:
        raise HTTPException(status_code=400, detail="无法解析 YouTube URL")
    
    # 使用第三方 API（可以替换为其他可用的 API）
    # 这里暂时返回一个错误，提示用户使用 B站源
    raise HTTPException(
        status_code=400, 
        detail="YouTube 视频暂时无法解析，请尝试搜索 B站源"
    )