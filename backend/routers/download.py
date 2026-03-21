from fastapi import APIRouter, HTTPException, Response
from ..schemas.download import DownloadRequest, DownloadResponse
import subprocess
import os
import tempfile

router = APIRouter(prefix="/api/download", tags=["download"])

@router.get("/")
async def download_media(url: str, format: str = "video"):
    """
    下载媒体文件
    - url: 媒体 URL
    - format: 格式 (video, audio, best)
    - 使用 yt-dlp 获取媒体流
    - 设置 Content-Disposition 触发浏览器下载
    """
    try:
        import yt_dlp
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # yt-dlp 选项
        ydl_opts = {
            'format': 'best' if format == 'best' else ('bestvideo+bestaudio/best' if format == 'video' else 'bestaudio/best'),
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        # 下载媒体
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # 获取下载的文件路径
            filename = ydl.prepare_filename(info)
            
            # 处理合并的音视频
            if format == 'video' and info.get('requested_formats'):
                # 检查是否需要合并
                ext = info.get('ext', 'mp4')
                if ext not in ['mp4', 'webm', 'mkv']:
                    ext = 'mp4'
                filename = os.path.join(temp_dir, f"{info.get('title', 'media')}.{ext}")
        
        # 读取文件内容
        if not os.path.exists(filename):
            # 尝试查找文件
            for f in os.listdir(temp_dir):
                if os.path.isfile(os.path.join(temp_dir, f)):
                    filename = os.path.join(temp_dir, f)
                    break
        
        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="Download failed")
        
        with open(filename, 'rb') as f:
            content = f.read()
        
        # 获取文件名
        download_filename = os.path.basename(filename)
        
        # 清理临时文件（可选，生产环境应该用后台任务清理）
        try:
            os.remove(filename)
            os.rmdir(temp_dir)
        except:
            pass
        
        # 返回文件
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{download_filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.post("/", response_model=DownloadResponse)
async def download_media_post(request: DownloadRequest):
    """
    下载媒体文件（POST 方式）
    """
    try:
        import yt_dlp
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # yt-dlp 选项
        ydl_opts = {
            'format': 'best' if request.format == 'best' else ('bestvideo+bestaudio/best' if request.format == 'video' else 'bestaudio/best'),
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        # 下载媒体
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            filename = ydl.prepare_filename(info)
        
        # 获取文件名
        download_filename = os.path.basename(filename)
        
        # 返回下载信息（实际下载由前端处理）
        return {
            "success": True,
            "download_url": f"/api/download/?url={request.url}&format={request.format}",
            "filename": download_filename
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
