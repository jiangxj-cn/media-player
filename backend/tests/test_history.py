"""
历史记录 API 测试
"""

import pytest


class TestHistoryAPI:
    """历史记录接口测试"""
    
    def test_get_history_unauthorized(self, client):
        """测试未认证获取历史"""
        response = client.get("/api/history")
        assert response.status_code == 401
    
    def test_get_history_authorized(self, client, auth_headers):
        """测试认证后获取历史"""
        response = client.get("/api/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_add_history_unauthorized(self, client):
        """测试未认证添加历史"""
        response = client.post(
            "/api/history",
            json={
                "media_id": "hist123",
                "title": "History Item",
                "url": "https://example.com/video",
                "source": "youtube",
                "position": 30
            }
        )
        assert response.status_code == 401
    
    def test_add_history_authorized(self, client, auth_headers):
        """测试认证后添加历史"""
        response = client.post(
            "/api/history",
            json={
                "media_id": "hist123",
                "title": "History Item",
                "url": "https://example.com/video",
                "source": "youtube",
                "position": 30
            },
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_clear_history(self, client, auth_headers):
        """测试清空历史"""
        # 添加一些历史
        client.post(
            "/api/history",
            json={
                "media_id": "clear_test",
                "title": "To Clear",
                "url": "https://example.com/video",
                "source": "youtube",
                "position": 0
            },
            headers=auth_headers
        )
        
        # 清空历史
        response = client.delete("/api/history", headers=auth_headers)
        assert response.status_code in [200, 204]