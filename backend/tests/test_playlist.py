"""
播放列表 API 测试
"""

import pytest


class TestPlaylistAPI:
    """播放列表接口测试"""
    
    def test_get_playlists_structure(self, client):
        """测试获取播放列表响应结构"""
        response = client.get("/api/playlists/")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "playlists" in data
        assert isinstance(data["playlists"], list)
    
    def test_create_playlist(self, client):
        """测试创建播放列表"""
        response = client.post(
            "/api/playlists/",
            json={"name": "My Playlist"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "My Playlist"
    
    def test_get_playlist_by_id(self, client):
        """测试获取单个播放列表"""
        # 先创建
        create_response = client.post(
            "/api/playlists/",
            json={"name": "Test Playlist"}
        )
        playlist_id = create_response.json().get("id")
        
        if playlist_id:
            # 获取
            get_response = client.get(f"/api/playlists/{playlist_id}")
            assert get_response.status_code == 200
            assert get_response.json()["name"] == "Test Playlist"
    
    def test_update_playlist(self, client):
        """测试更新播放列表"""
        # 创建播放列表
        create_response = client.post(
            "/api/playlists/",
            json={"name": "Original Name"}
        )
        playlist_id = create_response.json().get("id")
        
        if playlist_id:
            # 更新播放列表
            update_response = client.put(
                f"/api/playlists/{playlist_id}",
                json={"name": "Updated Name"}
            )
            assert update_response.status_code == 200
            assert update_response.json()["name"] == "Updated Name"
    
    def test_delete_playlist(self, client):
        """测试删除播放列表"""
        # 创建播放列表
        create_response = client.post(
            "/api/playlists/",
            json={"name": "To Delete"}
        )
        playlist_id = create_response.json().get("id")
        
        if playlist_id:
            # 删除播放列表
            delete_response = client.delete(
                f"/api/playlists/{playlist_id}"
            )
            assert delete_response.status_code == 200
            
            # 验证已删除
            get_response = client.get(f"/api/playlists/{playlist_id}")
            assert get_response.status_code == 404
    
    def test_add_item_to_playlist(self, client):
        """测试添加项到播放列表"""
        # 创建播放列表
        create_response = client.post(
            "/api/playlists/",
            json={"name": "Item Test Playlist"}
        )
        playlist_id = create_response.json().get("id")
        
        if playlist_id:
            # 添加项
            add_response = client.post(
                f"/api/playlists/{playlist_id}/items",
                json={
                    "media_url": "https://youtube.com/watch?v=item1",
                    "title": "Test Item",
                    "source": "youtube"
                }
            )
            assert add_response.status_code == 200
            assert add_response.json()["title"] == "Test Item"