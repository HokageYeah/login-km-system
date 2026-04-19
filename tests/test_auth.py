"""
认证模块测试
"""
import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """认证相关测试"""
    
    def test_register_success(self, client):
        """测试用户注册成功"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "haha",
                "password": "password123"
            }
        )
        
        # 由于响应格式可能被中间件处理，需要适配实际返回格式
        # 这里假设成功返回200状态码
        assert response.status_code in [200, 201]
    
    def test_register_duplicate_username(self, client, test_user):
        """测试重复用户名注册"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",  # 已存在的用户名
                "password": "password123"
            }
        )
        
        # 应该返回错误
        assert response.status_code in [400, 422]

    def test_register_username_too_short_returns_chinese_validation_error(self, client):
        """测试注册用户名过短时返回清晰的中文校验提示"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "yy",
                "password": "password123"
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert data["ret"][0].startswith("ERROR::请求参数校验失败")
        assert "用户名长度不能少于 3 个字符" in data["ret"][0]
        assert data["data"]["errors"][0]["field"] == "username"

    def test_register_username_invalid_character_returns_chinese_validation_error(self, client):
        """测试注册用户名包含非法字符时返回清晰的中文校验提示"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "abc-123",
                "password": "password123"
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert "用户名只能包含字母、数字和下划线" in data["ret"][0]
        assert data["data"]["errors"][0]["field"] == "username"
    
    def test_login_success(self, client, test_user, test_app):
        """测试用户登录成功"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "test123456",
                "app_key": "test_app",
                "device_id": "test_device_001"
            }
        )
        
        assert response.status_code == 200
        # 根据实际响应格式验证
        # data = response.json()
        # assert "token" in data or ("data" in data and "token" in data["data"])
    
    def test_login_wrong_password(self, client, test_user, test_app):
        """测试错误密码登录"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword",
                "app_key": "test_app",
                "device_id": "test_device_001"
            }
        )
        
        # 应该返回错误
        assert response.status_code in [400, 401]
    
    def test_login_nonexistent_user(self, client, test_app):
        """测试不存在的用户登录"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123",
                "app_key": "test_app",
                "device_id": "test_device_001"
            }
        )
        
        # 应该返回错误
        assert response.status_code in [400, 401, 404]
    
    def test_login_missing_params(self, client):
        """测试缺少参数的登录请求"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123"
                # 缺少 app_key 和 device_id
            }
        )
        
        # 应该返回参数错误
        assert response.status_code == 422


@pytest.mark.asyncio
class TestAuthService:
    """AuthService 测试"""
    
    def test_password_hashing(self):
        """测试密码哈希"""
        from app.utils.security import hash_password, verify_password
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        # 验证密码哈希
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
    
    def test_token_creation(self):
        """测试Token生成"""
        from app.utils.security import create_access_token, decode_access_token
        
        data = {
            "user_id": 1,
            "username": "testuser",
            "role": "user"
        }
        
        token = create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        
        # 解码Token
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["user_id"] == 1
        assert decoded["username"] == "testuser"

    def test_admin_login_without_card_returns_has_card_true(self, db_session, test_admin, test_app):
        """测试管理员登录时无需绑定卡密也返回可访问状态"""
        from app.services.auth_service import AuthService

        auth_service = AuthService(db_session)

        token, user_info, error = auth_service.login(
            username=test_admin.username,
            password="adminpass123",
            app_key=test_app.app_key,
            device_id="admin_device_001"
        )

        assert error is None
        assert token is not None
        assert user_info["role"] == "admin"
        assert user_info["has_card"] is True
