"""
收藏 API 测试
"""

import pytest


class TestFavoritesAPI:
    """收藏接口测试"""
    
    def test_get_favorites_structure(self, client):
        """测试获取收藏响应结构"""
        response = client.get("/api/favorites/")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "favorites" in data
    
    def test_add_favorite_structure(self, client):
        """测试添加收藏响应结构"""
        response = client.post(
            "/api/favorites/",
            json={
                "media_url": "https://youtube.com/watch?v=test123",
                "title": "Test Video",
                "thumbnail": "https://example.com/thumb.jpg",
                "source": "youtube"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Video"
    
    def test_add_duplicate_favorite(self, client):
        """测试重复添加收藏"""
        # 第一次添加
        client.post(
            "/api/favorites/",
            json={
                "media_url": "https://youtube.com/watch?v=dup",
                "title": "Duplicate Test",
                "source": "youtube"
            }
        )
        
        # 第二次添加相同 URL
        response = client.post(
            "/api/favorites/",
            json={
                "media_url": "https://youtube.com/watch?v=dup",
                "title": "Duplicate Test",
                "source": "youtube"
            }
        )
        assert response.status_code == 400  # Already favorited
    
    def test_remove_favorite(self, client):
        """测试移除收藏"""
        # 先添加收藏
        add_response = client.post(
            "/api/favorites/",
            json={
                "media_url": "https://youtube.com/watch?v=remove",
                "title": "To Remove",
                "source": "youtube"
            }
        )
        favorite_id = add_response.json().get("id")
        
        if favorite_id:
            # 移除收藏
            remove_response = client.delete(f"/api/favorites/{favorite_id}")
            assert remove_response.status_code == 200