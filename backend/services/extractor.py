from fastapi import HTTPException
import subprocess
import json

def extract_media_info(url: str, format_type: str = "best"):
    """提取媒体信息 - 使用 yt-dlp 命令行工具"""
    
    # 使用命令行方式，更稳定
    cmd = [
        'yt-dlp',
        '--no-warnings',
        '--quiet',
        '--dump-json',
        '--no-playlist',
        '-f', 'best[ext=mp4]/best',
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            # 如果失败，尝试不指定格式
            cmd = ['yt-dlp', '--no-warnings', '--quiet', '--dump-json', '--no-playlist', url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                raise Exception(f"yt-dlp failed: {result.stderr}")
        
        info = json.loads(result.stdout)
        
        # 获取直接播放 URL
        direct_url = info.get('url')
        
        # 如果没有 url，尝试从 formats 中获取
        if not direct_url:
            for f in info.get('formats', []):
                if f.get('url') and f.get('vcodec') != 'none':
                    direct_url = f['url']
                    break
        
        return {
            'title': info.get('title', 'Unknown'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration'),
            'uploader': info.get('uploader'),
            'direct_url': direct_url,
            'original_url': url,
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="提取超时")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="解析失败")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))