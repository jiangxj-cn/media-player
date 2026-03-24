"""
媒体提取服务 - 支持多平台视频解析
使用 yt-dlp 作为主要解析器，支持 B站、抖音、西瓜、优酷、YouTube 等
"""

from fastapi import HTTPException
import yt_dlp
import asyncio
import re
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# 线程池执行器
executor = ThreadPoolExecutor(max_workers=8)


@dataclass
class VideoFormat:
    """视频格式信息"""
    format_id: str
    ext: str
    quality: str  # 'low', 'medium', 'high', 'best'
    resolution: Optional[str]
    filesize: Optional[int]
    vcodec: Optional[str]
    acodec: Optional[str]
    url: Optional[str]


@dataclass
class VideoInfo:
    """视频信息"""
    title: str
    thumbnail: str
    duration: int
    uploader: str
    source: str
    original_url: str
    direct_url: Optional[str] = None
    formats: List[VideoFormat] = None
    description: Optional[str] = None


# 支持的平台映射
SUPPORTED_PLATFORMS = {
    # 国内平台
    'bilibili.com': 'bilibili',
    'b23.tv': 'bilibili',
    'douyin.com': 'douyin',
    'iesdouyin.com': 'douyin',
    'ixigua.com': 'ixigua',
    'toutiao.com': 'toutiao',
    'youku.com': 'youku',
    'v.youku.com': 'youku',
    # 国际平台
    'youtube.com': 'youtube',
    'youtu.be': 'youtube',
    'tiktok.com': 'tiktok',
    'twitter.com': 'twitter',
    'x.com': 'twitter',
    'vimeo.com': 'vimeo',
    'facebook.com': 'facebook',
    'instagram.com': 'instagram',
}


def detect_platform(url: str) -> Optional[str]:
    """检测 URL 所属平台"""
    url_lower = url.lower()
    for domain, platform in SUPPORTED_PLATFORMS.items():
        if domain in url_lower:
            return platform
    return 'generic'  # 尝试通用解析


def get_yt_dlp_opts(format_type: str = "best", extract_flat: bool = False) -> dict:
    """获取 yt-dlp 配置选项"""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': extract_flat,
        'noplaylist': True,
        'socket_timeout': 30,
        'retries': 3,
        # 添加更多 User-Agent 和 Headers
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
        },
        # 地理位置绑定（某些平台需要）
        'geo_bypass': True,
        'geo_bypass_country': 'CN',
    }
    
    if format_type == "best":
        opts['format'] = 'bestvideo+bestaudio/best'
    elif format_type == "medium":
        opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
    elif format_type == "low":
        opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
    elif format_type == "audio":
        opts['format'] = 'bestaudio/best'
    elif format_type == "list":
        # 获取所有格式列表
        opts['format'] = 'all'
        opts['listformats'] = True
    
    return opts


def extract_with_yt_dlp(url: str, format_type: str = "best") -> VideoInfo:
    """使用 yt-dlp 提取视频信息"""
    platform = detect_platform(url)
    opts = get_yt_dlp_opts(format_type)
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                raise HTTPException(status_code=400, detail="无法获取视频信息")
            
            # 提取格式列表
            formats = []
            if 'formats' in info:
                for f in info['formats']:
                    if f.get('url') or f.get('manifest_url'):
                        quality = 'medium'
                        height = f.get('height', 0)
                        if height and height >= 1080:
                            quality = 'high'
                        elif height and height >= 720:
                            quality = 'medium'
                        elif height and height >= 480:
                            quality = 'low'
                        else:
                            quality = 'low'
                        
                        formats.append(VideoFormat(
                            format_id=f.get('format_id', ''),
                            ext=f.get('ext', 'mp4'),
                            quality=quality,
                            resolution=f"{f.get('width', 0)}x{f.get('height', 0)}" if f.get('width') else None,
                            filesize=f.get('filesize') or f.get('filesize_approx'),
                            vcodec=f.get('vcodec', ''),
                            acodec=f.get('acodec', ''),
                            url=f.get('url') or f.get('manifest_url')
                        ))
            
            # 排序格式（高质量优先）
            quality_order = {'high': 3, 'medium': 2, 'low': 1}
            formats.sort(key=lambda x: quality_order.get(x.quality, 0), reverse=True)
            
            # 获取最佳 URL
            direct_url = None
            if info.get('url'):
                direct_url = info['url']
            elif info.get('manifest_url'):
                direct_url = info['manifest_url']
            elif formats:
                # 找到有 URL 的最佳格式
                for f in formats:
                    if f.url and 'm3u8' in str(f.url).lower():
                        direct_url = f.url
                        break
                if not direct_url and formats:
                    direct_url = formats[0].url
            
            return VideoInfo(
                title=info.get('title', 'Unknown'),
                thumbnail=info.get('thumbnail', info.get('thumbnails', [{}])[-1].get('url', '') if info.get('thumbnails') else ''),
                duration=info.get('duration', 0),
                uploader=info.get('uploader', info.get('channel', '')),
                source=platform,
                original_url=url,
                direct_url=direct_url,
                formats=formats[:20] if formats else None,  # 限制格式数量
                description=info.get('description', '')[:500] if info.get('description') else None
            )
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'Unsupported URL' in error_msg or 'not supported' in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"不支持的视频源: {platform}")
        elif 'Video unavailable' in error_msg or 'Private video' in error_msg:
            raise HTTPException(status_code=403, detail="视频不可用或为私密视频")
        elif 'Sign in' in error_msg or 'login' in error_msg.lower():
            raise HTTPException(status_code=401, detail="需要登录才能访问此视频")
        else:
            logger.error(f"yt-dlp extract error: {error_msg}")
            raise HTTPException(status_code=400, detail=f"解析失败: {error_msg[:100]}")
    except Exception as e:
        logger.error(f"Unexpected error extracting {url}: {e}")
        raise HTTPException(status_code=500, detail=f"解析服务异常: {str(e)[:50]}")


def extract_media_info(url: str, format_type: str = "best") -> dict:
    """提取媒体信息 - 主入口函数（兼容旧 API）"""
    info = extract_with_yt_dlp(url, format_type)
    
    result = {
        'title': info.title,
        'thumbnail': info.thumbnail,
        'duration': info.duration,
        'uploader': info.uploader,
        'source': info.source,
        'original_url': info.original_url,
        'direct_url': info.direct_url,
    }
    
    # 添加格式列表（如果有）
    if info.formats:
        result['formats'] = [
            {
                'format_id': f.format_id,
                'ext': f.ext,
                'quality': f.quality,
                'resolution': f.resolution,
                'filesize': f.filesize,
                'url': f.url
            }
            for f in info.formats if f.url
        ]
    
    return result


def extract_formats_only(url: str) -> List[dict]:
    """仅提取格式列表（用于质量选择）"""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'noplaylist': True,
        'socket_timeout': 30,
    }
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            seen_resolutions = set()
            
            for f in info.get('formats', []):
                height = f.get('height')
                if not height or height < 240:
                    continue
                    
                # 去重相同分辨率
                res_key = f.get('format_id', '')[:10]
                if res_key in seen_resolutions:
                    continue
                seen_resolutions.add(res_key)
                
                # 只保留视频+音频组合格式或单独的完整格式
                vcodec = f.get('vcodec', 'none')
                acodec = f.get('acodec', 'none')
                
                if vcodec != 'none' or acodec != 'none':
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext', 'mp4'),
                        'resolution': f"{f.get('width', 0)}x{height}",
                        'height': height,
                        'fps': f.get('fps'),
                        'filesize': f.get('filesize') or f.get('filesize_approx'),
                        'vcodec': vcodec,
                        'acodec': acodec,
                        'url': f.get('url'),
                    })
            
            # 按分辨率排序
            formats.sort(key=lambda x: x.get('height', 0), reverse=True)
            return formats[:15]  # 限制返回数量
            
    except Exception as e:
        logger.error(f"Failed to extract formats: {e}")
        return []


async def extract_media_info_async(url: str, format_type: str = "best") -> dict:
    """异步版本的提取函数"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, extract_media_info, url, format_type)


async def extract_formats_async(url: str) -> List[dict]:
    """异步版本的质量列表提取"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, extract_formats_only, url)


# 支持的源列表 API
def get_supported_sources() -> List[dict]:
    """返回支持的源列表"""
    return [
        {'name': 'B站', 'domains': ['bilibili.com', 'b23.tv'], 'icon': '📺'},
        {'name': '抖音', 'domains': ['douyin.com', 'iesdouyin.com'], 'icon': '🎵'},
        {'name': '西瓜视频', 'domains': ['ixigua.com'], 'icon': '🍉'},
        {'name': '头条', 'domains': ['toutiao.com'], 'icon': '📰'},
        {'name': '优酷', 'domains': ['youku.com', 'v.youku.com'], 'icon': '🎬'},
        {'name': 'YouTube', 'domains': ['youtube.com', 'youtu.be'], 'icon': '▶️'},
        {'name': 'TikTok', 'domains': ['tiktok.com'], 'icon': '🎶'},
        {'name': 'Twitter/X', 'domains': ['twitter.com', 'x.com'], 'icon': '🐦'},
        {'name': 'Vimeo', 'domains': ['vimeo.com'], 'icon': '🎥'},
        {'name': '更多...', 'domains': ['其他 yt-dlp 支持的平台'], 'icon': '🌐'},
    ]