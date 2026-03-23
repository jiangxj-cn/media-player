"""
收藏 API 测试
"""

import pytest


class TestFavoritesAPI:
    """收藏接口测试"""
    
    def test_get_favorites_unauthorized(self, client):
        """测试未认证获取收藏"""
        response = client.get("/api/favorites")
        assert response.status_code == 401
    
    def test_get_favorites_authorized(self, client, auth_headers):
        """测试认证后获取收藏"""
        response = client.get("/api/favorites", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_add_favorite_unauthorized(self, client):
        """测试未认证添加收藏"""
        response = client.post(
            "/api/favorites",
            json={
                "media_id": "test123",
                "title": "Test Video",
                "url": "https://example.com/video",
                "source": "youtube"
            }
        )
        assert response.status_code == 401
    
    def test_add_favorite_authorized(self, client, auth_headers):
        """测试认证后添加收藏"""
        response = client.post(
            "/api/favorites",
            json={
                "media_id": "test123",
                "title": "Test Video",
                "url": "https://example.com/video",
                "source": "youtube"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_remove_favorite(self, client, auth_headers):
        """测试移除收藏"""
        # 先添加收藏
        add_response = client.post(
            "/api/favorites",
            json={
                "media_id": "remove_test",
                "title": "To Remove",
                "url": "https://example.com/video",
                "source": "youtube"
            },
            headers=auth_headers
        )
        
        # 移除收藏
        remove_response = client.delete(
            "/api/favorites/remove_test",
            headers=auth_headers
        )
        assert remove_response.status_code in [200, 204, 404]