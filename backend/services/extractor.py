from fastapi import HTTPException
import yt_dlp

def extract_media_info(url: str, format_type: str = "best"):
    """提取媒体信息"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            result = {
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'formats': [],
            }
            
            # 获取最佳视频 + 音频
            if format_type in ['best', 'video']:
                for f in info.get('formats', []):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        if f.get('url'):
                            result['direct_url'] = f['url']
                            break
                
                # 如果没找到合并流，分别获取视频和音频
                if not result.get('direct_url'):
                    video_url = None
                    audio_url = None
                    
                    for f in info.get('formats', []):
                        if f.get('vcodec') != 'none' and f.get('url'):
                            video_url = f['url']
                        if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url'):
                            audio_url = f['url']
                    
                    if video_url:
                        result['direct_url'] = video_url
                    if audio_url:
                        result['audio_url'] = audio_url
            
            # 仅音频
            elif format_type == 'audio':
                for f in info.get('formats', []):
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        if f.get('url'):
                            result['audio_url'] = f['url']
                            break
            
            # 获取可用格式列表
            for f in info.get('formats', [])[:10]:
                if f.get('url'):
                    result['formats'].append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f.get('resolution') or f.get('height'),
                        'filesize': f.get('filesize'),
                        'url': f.get('url'),
                    })
            
            return result
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
