"""
API Response Time Monitoring Middleware
记录每个 API 请求的响应时间
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# 响应时间统计
response_times: dict[str, list[float]] = {}

class TimingMiddleware(BaseHTTPMiddleware):
    """API 响应时间监控中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录开始时间
        start_time = time.perf_counter()
        
        # 调用下一个中间件或路由处理器
        response = await call_next(request)
        
        # 计算响应时间
        duration = (time.perf_counter() - start_time) * 1000  # 转换为毫秒
        
        # 记录响应时间
        path = request.url.path
        if path.startswith('/api/'):
            # 存储响应时间用于统计
            if path not in response_times:
                response_times[path] = []
            response_times[path].append(duration)
            
            # 只保留最近 100 次请求
            if len(response_times[path]) > 100:
                response_times[path] = response_times[path][-100:]
            
            # 添加响应头
            response.headers["X-Response-Time"] = f"{duration:.2f}ms"
            
            # 日志记录慢请求 (>1秒)
            if duration > 1000:
                logger.warning(f"Slow request: {request.method} {path} took {duration:.2f}ms")
            else:
                logger.debug(f"{request.method} {path} - {duration:.2f}ms")
        
        return response


def get_api_stats() -> dict:
    """获取 API 统计信息"""
    stats = {}
    for path, times in response_times.items():
        if times:
            stats[path] = {
                "count": len(times),
                "avg_ms": sum(times) / len(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "p95_ms": sorted(times)[int(len(times) * 0.95)] if len(times) > 20 else max(times),
            }
    return stats


def get_health_status() -> dict:
    """获取健康状态"""
    stats = get_api_stats()
    slow_endpoints = []
    
    for path, data in stats.items():
        if data["avg_ms"] > 500:  # 平均响应时间 > 500ms
            slow_endpoints.append({
                "path": path,
                "avg_ms": data["avg_ms"]
            })
    
    return {
        "status": "degraded" if slow_endpoints else "healthy",
        "slow_endpoints": slow_endpoints,
        "total_endpoints": len(stats)
    }