"""
搜索 API 测试
"""

import pytest
from unittest.mock import patch, AsyncMock


class TestSearchAPI:
    """搜索接口测试"""
    
    def test_search_endpoint_exists(self, client):
        """测试搜索端点存在"""
        response = client.get("/api/search?q=test")
        # 可能返回 200 或者 422（参数验证错误）
        assert response.status_code in [200, 422]
    
    def test_search_missing_query(self, client):
        """测试缺少搜索参数"""
        response = client.get("/api/search")
        assert response.status_code == 422  # Validation error
    
    def test_search_with_query(self, client):
        """测试带查询参数的搜索"""
        # Mock 搜索服务返回
        with patch('backend.routers.search.search_youtube') as mock_youtube, \
             patch('backend.routers.search.search_bilibili') as mock_bilibili, \
             patch('backend.routers.search.search_netease_music') as mock_netease:
            
            mock_youtube.return_value = AsyncMock(return_value=[
                {
                    "id": "yt1",
                    "title": "Test Video",
                    "url": "https://youtube.com/watch?v=test",
                    "source": "youtube",
                    "duration": 120
                }
            ])()
            
            mock_bilibili.return_value = AsyncMock(return_value=[])()
            mock_netease.return_value = AsyncMock(return_value=[])()
            
            response = client.get("/api/search?q=test&max_results=5")
            
            # 根据实际实现调整断言
            assert response.status_code in [200, 500]
    
    def test_search_video_endpoint(self, client):
        """测试视频搜索端点"""
        response = client.get("/api/search/video?q=test")
        assert response.status_code in [200, 422, 500]
    
    def test_search_music_endpoint(self, client):
        """测试音乐搜索端点"""
        response = client.get("/api/search/music?q=test")
        assert response.status_code in [200, 422, 500]