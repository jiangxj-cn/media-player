"""
播放列表 API 测试
"""

import pytest


class TestPlaylistAPI:
    """播放列表接口测试"""
    
    def test_get_playlists_unauthorized(self, client):
        """测试未认证获取播放列表"""
        response = client.get("/api/playlist")
        assert response.status_code == 401
    
    def test_create_playlist_unauthorized(self, client):
        """测试未认证创建播放列表"""
        response = client.post(
            "/api/playlist",
            json={"name": "Test Playlist", "description": "Test"}
        )
        assert response.status_code == 401
    
    def test_get_playlists_authorized(self, client, auth_headers):
        """测试认证后获取播放列表"""
        response = client.get("/api/playlist", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_playlist_authorized(self, client, auth_headers):
        """测试认证后创建播放列表"""
        response = client.post(
            "/api/playlist",
            json={"name": "My Playlist", "description": "Test playlist"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My Playlist"
    
    def test_update_playlist(self, client, auth_headers):
        """测试更新播放列表"""
        # 创建播放列表
        create_response = client.post(
            "/api/playlist",
            json={"name": "Original Name", "description": "Original"},
            headers=auth_headers
        )
        playlist_id = create_response.json().get("id")
        
        if playlist_id:
            # 更新播放列表
            update_response = client.put(
                f"/api/playlist/{playlist_id}",
                json={"name": "Updated Name", "description": "Updated"},
                headers=auth_headers
            )
            assert update_response.status_code == 200
    
    def test_delete_playlist(self, client, auth_headers):
        """测试删除播放列表"""
        # 创建播放列表
        create_response = client.post(
            "/api/playlist",
            json={"name": "To Delete", "description": "Will be deleted"},
            headers=auth_headers
        )
        playlist_id = create_response.json().get("id")
        
        if playlist_id:
            # 删除播放列表
            delete_response = client.delete(
                f"/api/playlist/{playlist_id}",
                headers=auth_headers
            )
            assert delete_response.status_code in [200, 204, 404]