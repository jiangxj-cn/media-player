"""
认证 API 测试
"""

import pytest


class TestAuthAPI:
    """认证接口测试"""
    
    def test_register_success(self, client, test_user_data):
        """测试用户注册成功"""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
    
    def test_register_duplicate_username(self, client, test_user_data):
        """测试重复用户名注册"""
        # 第一次注册
        client.post("/api/auth/register", json=test_user_data)
        
        # 第二次注册相同用户名
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 400
    
    def test_login_success(self, client, test_user_data):
        """测试登录成功"""
        # 先注册
        client.post("/api/auth/register", json=test_user_data)
        
        # 登录
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user_data):
        """测试密码错误"""
        # 先注册
        client.post("/api/auth/register", json=test_user_data)
        
        # 错误密码登录
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """测试不存在用户登录"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "anypassword"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """测试获取当前用户"""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
    
    def test_get_current_user_unauthorized(self, client):
        """测试未认证访问"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401