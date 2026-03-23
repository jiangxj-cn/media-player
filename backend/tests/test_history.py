"""
历史记录 API 测试
"""

import pytest


class TestHistoryAPI:
    """历史记录接口测试"""
    
    def test_get_history_structure(self, client):
        """测试获取历史响应结构"""
        response = client.get("/api/history/")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "history" in data
        assert isinstance(data["history"], list)
    
    def test_add_history_record(self, client):
        """测试添加历史记录"""
        response = client.post(
            "/api/history/",
            json={
                "media_url": "https://youtube.com/watch?v=hist123",
                "title": "History Item",
                "position": 30,
                "duration": 180,
                "source": "youtube"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["position"] == 30
    
    def test_update_history_position(self, client):
        """测试更新历史播放位置"""
        # 第一次记录
        client.post(
            "/api/history/",
            json={
                "media_url": "https://youtube.com/watch?v=update",
                "title": "Update Test",
                "position": 10,
                "source": "youtube"
            }
        )
        
        # 更新位置
        response = client.post(
            "/api/history/",
            json={
                "media_url": "https://youtube.com/watch?v=update",
                "title": "Update Test",
                "position": 50,
                "source": "youtube"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["position"] == 50
    
    def test_clear_history(self, client):
        """测试清空历史"""
        # 添加一些历史
        client.post(
            "/api/history/",
            json={
                "media_url": "https://youtube.com/watch?v=clear",
                "title": "To Clear",
                "position": 0,
                "source": "youtube"
            }
        )
        
        # 清空历史
        response = client.delete("/api/history/")
        assert response.status_code == 200
        assert response.json()["message"] == "History cleared"
        
        # 验证已清空
        get_response = client.get("/api/history/")
        assert get_response.json()["total"] == 0