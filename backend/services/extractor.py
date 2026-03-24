"""
媒体提取服务 - 支持多平台视频解析

策略:
1. YouTube 和 B站：使用官方 iframe 嵌入播放器（最可靠，绕过反爬）
2. 其他平台：使用 yt-dlp 尝试解析
3. 提供备用方案和错误提示
"""

from fastapi import HTTPException
import yt_dlp
import asyncio
import re
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import logging
import urllib.parse

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
    embed_url: Optional[str] = None  # iframe 嵌入地址
    use_embed: bool = False  # 是否使用 iframe 播放
    formats: List[VideoFormat] = None
    description: Optional[str] = None
    piped_url: Optional[str] = None  # Piped 代理链接（用于中国大陆用户访问 YouTube）


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


def extract_youtube_video_id(url: str) -> Optional[str]:
    """从 YouTube URL 提取视频 ID"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_bilibili_video_id(url: str) -> Optional[Dict[str, str]]:
    """从 B站 URL 提取视频 ID (BV 号或 AV 号)"""
    # BV 号
    bv_match = re.search(r'BV([a-zA-Z0-9]+)', url)
    if bv_match:
        return {'bvid': f'BV{bv_match.group(1)}'}
    
    # AV 号
    av_match = re.search(r'av(\d+)', url, re.IGNORECASE)
    if av_match:
        return {'avid': av_match.group(1)}
    
    # b23.tv 短链接需要解析，这里返回原始 URL
    if 'b23.tv' in url:
        return {'short_url': url}
    
    return None


# YouTube 代理实例列表（Piped/Invidious）
# 在中国大陆可用的 YouTube 前端代理
YOUTUBE_PROXY_INSTANCES = [
    "piped.video",      # Piped - 主要实例
    "piped.kavin.rocks", # Piped - 备用实例
]


def get_youtube_embed_url(video_id: str) -> str:
    """获取 YouTube 嵌入播放器 URL"""
    return f"https://www.youtube.com/embed/{video_id}?autoplay=1&rel=0"


def get_piped_embed_url(video_id: str) -> str:
    """获取 Piped 代理嵌入播放器 URL（用于中国大陆用户）"""
    # 使用 piped.video 作为主要实例
    return f"https://piped.video/embed/{video_id}"


def get_bilibili_embed_url(video_info: Dict[str, str]) -> str:
    """获取 B站 嵌入播放器 URL"""
    if 'bvid' in video_info:
        return f"https://player.bilibili.com/player.html?bvid={video_info['bvid']}&autoplay=1&high_quality=1&danmaku=0"
    elif 'avid' in video_info:
        return f"https://player.bilibili.com/player.html?aid={video_info['avid']}&autoplay=1&high_quality=1&danmaku=0"
    return ""


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
        opts['format'] = 'all'
        opts['listformats'] = True
    
    return opts


def extract_youtube_info(url: str) -> VideoInfo:
    """提取 YouTube 视频信息 - 使用服务器代理流"""
    video_id = extract_youtube_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="无法解析 YouTube 链接")
    
    # 使用服务器代理 URL（中国大陆可访问）
    proxy_stream_url = f"/api/youtube/{video_id}/stream"
    thumbnail = f"/api/youtube/{video_id}/thumbnail"  # 也代理缩略图
    
    # 备用：YouTube 官方嵌入 URL（需要 VPN）
    embed_url = get_youtube_embed_url(video_id)
    piped_url = get_piped_embed_url(video_id)
    
    return VideoInfo(
        title=f"YouTube 视频 ({video_id})",
        thumbnail=thumbnail,
        duration=0,
        uploader="YouTube",
        source="youtube",
        original_url=url,
        direct_url=proxy_stream_url,  # 使用代理流 URL
        embed_url=embed_url,
        use_embed=False,  # 不再使用 iframe，改用原生播放器
        description=None,
        piped_url=piped_url
    )


def extract_bilibili_info(url: str) -> VideoInfo:
    """提取 B站 视频信息 - 使用 iframe 嵌入"""
    video_info = extract_bilibili_video_id(url)
    if not video_info:
        raise HTTPException(status_code=400, detail="无法解析 B站 链接")
    
    embed_url = get_bilibili_embed_url(video_info)
    if not embed_url:
        # 对于 b23.tv 短链接，直接使用原始 URL
        embed_url = f"//player.bilibili.com/player.html?bvid=&autoplay=1"
    
    return VideoInfo(
        title="B站 视频",
        thumbnail="",
        duration=0,
        uploader="B站",
        source="bilibili",
        original_url=url,
        direct_url=None,
        embed_url=embed_url,
        use_embed=True,
        description=None
    )


def extract_with_yt_dlp(url: str, format_type: str = "best") -> VideoInfo:
    """使用 yt-dlp 提取视频信息（用于其他平台）"""
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
                embed_url=None,
                use_embed=False,
                formats=formats[:20] if formats else None,
                description=info.get('description', '')[:500] if info.get('description') else None
            )
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'Unsupported URL' in error_msg or 'not supported' in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"不支持的视频源: {platform}")
        elif 'Video unavailable' in error_msg or 'Private video' in error_msg:
            raise HTTPException(status_code=403, detail="视频不可用或为私密视频")
        elif 'Sign in' in error_msg or 'login' in error_msg.lower() or '412' in error_msg:
            raise HTTPException(status_code=401, detail="视频需要登录或被反爬限制，请尝试使用嵌入播放器")
        else:
            logger.error(f"yt-dlp extract error: {error_msg}")
            raise HTTPException(status_code=400, detail=f"解析失败: {error_msg[:100]}")
    except Exception as e:
        logger.error(f"Unexpected error extracting {url}: {e}")
        raise HTTPException(status_code=500, detail=f"解析服务异常: {str(e)[:50]}")


def extract_media_info(url: str, format_type: str = "best") -> dict:
    """提取媒体信息 - 主入口函数
    
    策略:
    1. YouTube/B站 -> 使用 iframe 嵌入（返回 embed_url）
    2. 其他平台 -> 使用 yt-dlp 尝试解析
    """
    platform = detect_platform(url)
    
    # YouTube 和 B站 使用 iframe 嵌入
    if platform == 'youtube':
        info = extract_youtube_info(url)
    elif platform == 'bilibili':
        info = extract_bilibili_info(url)
    else:
        # 其他平台使用 yt-dlp
        info = extract_with_yt_dlp(url, format_type)
    
    result = {
        'title': info.title,
        'thumbnail': info.thumbnail,
        'duration': info.duration,
        'uploader': info.uploader,
        'source': info.source,
        'original_url': info.original_url,
        'direct_url': info.direct_url,
        'embed_url': info.embed_url,
        'use_embed': info.use_embed,
    }
    
    # 添加 Piped 代理链接（仅 YouTube）
    if info.piped_url:
        result['piped_url'] = info.piped_url
    
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
    platform = detect_platform(url)
    
    # YouTube 和 B站 不需要格式选择，直接返回空
    if platform in ['youtube', 'bilibili']:
        return []
    
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
                    
                res_key = f.get('format_id', '')[:10]
                if res_key in seen_resolutions:
                    continue
                seen_resolutions.add(res_key)
                
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
            
            formats.sort(key=lambda x: x.get('height', 0), reverse=True)
            return formats[:15]
            
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
        {'name': 'B站', 'domains': ['bilibili.com', 'b23.tv'], 'icon': '📺', 'note': '使用嵌入播放器'},
        {'name': '抖音', 'domains': ['douyin.com', 'iesdouyin.com'], 'icon': '🎵'},
        {'name': '西瓜视频', 'domains': ['ixigua.com'], 'icon': '🍉'},
        {'name': '头条', 'domains': ['toutiao.com'], 'icon': '📰'},
        {'name': '优酷', 'domains': ['youku.com', 'v.youku.com'], 'icon': '🎬'},
        {'name': 'YouTube', 'domains': ['youtube.com', 'youtu.be'], 'icon': '▶️', 'note': '使用嵌入播放器'},
        {'name': 'TikTok', 'domains': ['tiktok.com'], 'icon': '🎶'},
        {'name': 'Twitter/X', 'domains': ['twitter.com', 'x.com'], 'icon': '🐦'},
        {'name': 'Vimeo', 'domains': ['vimeo.com'], 'icon': '🎥'},
        {'name': '更多...', 'domains': ['其他 yt-dlp 支持的平台'], 'icon': '🌐'},
    ]