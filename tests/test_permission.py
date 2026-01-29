"""
权限校验模块测试
"""
import pytest
from datetime import datetime, timedelta


@pytest.mark.asyncio
class TestPermissionService:
    """PermissionService 测试"""
    
    def test_permission_check_no_card(self, db_session, test_user):
        """测试无卡密时的权限校验"""
        from app.services.permission_service import PermissionService
        
        permission_service = PermissionService(db_session)
        
        allowed, message, expire_time = permission_service.check_permission(
            user_id=test_user.id,
            device_id="test_device_001",
            permission="test_permission"
        )
        
        # 无卡密应该返回False
        assert allowed is False
        assert "未绑定卡密" in message
        assert expire_time is None
    
    def test_permission_check_with_valid_card(self, db_session, test_user, test_app):
        """测试有效卡密的权限校验"""
        from app.services.permission_service import PermissionService
        from app.models.card import Card, CardStatus
        from app.models.user_card import UserCard, UserCardStatus
        from app.models.card_device import CardDevice, CardDeviceStatus
        
        # 创建卡密
        card = Card(
            app_id=test_app.id,
            card_key="TEST-VALID-CARD-1234",
            status=CardStatus.USED,
            expire_time=datetime.now() + timedelta(days=30),
            max_device_count=2,
            permissions=["test_permission", "another_permission"]
        )
        db_session.add(card)
        db_session.commit()
        db_session.refresh(card)
        
        # 绑定卡密到用户
        user_card = UserCard(
            user_id=test_user.id,
            card_id=card.id,
            bind_time=datetime.now(),
            status=UserCardStatus.ACTIVE
        )
        db_session.add(user_card)
        
        # 绑定设备
        card_device = CardDevice(
            card_id=card.id,
            device_id="test_device_001",
            bind_time=datetime.now(),
            status=CardDeviceStatus.ACTIVE
        )
        db_session.add(card_device)
        db_session.commit()
        
        # 测试权限校验
        permission_service = PermissionService(db_session)
        
        # 有效权限
        allowed, message, expire_time = permission_service.check_permission(
            user_id=test_user.id,
            device_id="test_device_001",
            permission="test_permission"
        )
        assert allowed is True
        assert expire_time is not None
        
        # 无效权限
        allowed, message, expire_time = permission_service.check_permission(
            user_id=test_user.id,
            device_id="test_device_001",
            permission="nonexistent_permission"
        )
        assert allowed is False
        assert "权限配置不匹配" in message or "没有有效的卡密" in message
    
    def test_permission_check_expired_card(self, db_session, test_user, test_app):
        """测试过期卡密的权限校验"""
        from app.services.permission_service import PermissionService
        from app.models.card import Card, CardStatus
        from app.models.user_card import UserCard, UserCardStatus
        from app.models.card_device import CardDevice, CardDeviceStatus
        
        # 创建过期卡密
        card = Card(
            app_id=test_app.id,
            card_key="TEST-EXPIRED-CARD-1234",
            status=CardStatus.USED,
            expire_time=datetime.now() - timedelta(days=1),  # 已过期
            max_device_count=2,
            permissions=["test_permission"]
        )
        db_session.add(card)
        db_session.commit()
        db_session.refresh(card)
        
        # 绑定卡密和设备
        user_card = UserCard(
            user_id=test_user.id,
            card_id=card.id,
            bind_time=datetime.now(),
            status=UserCardStatus.ACTIVE
        )
        db_session.add(user_card)
        
        card_device = CardDevice(
            card_id=card.id,
            device_id="test_device_001",
            bind_time=datetime.now(),
            status=CardDeviceStatus.ACTIVE
        )
        db_session.add(card_device)
        db_session.commit()
        
        # 测试权限校验
        permission_service = PermissionService(db_session)
        
        allowed, message, expire_time = permission_service.check_permission(
            user_id=test_user.id,
            device_id="test_device_001",
            permission="test_permission"
        )
        
        # 过期卡密应该返回False
        assert allowed is False
        assert "已过期" in message or "没有有效的卡密" in message
        assert expire_time is None


class TestPermissionAPI:
    """权限API测试"""
    
    def test_permission_check_without_login(self, client):
        """测试未登录的权限校验"""
        response = client.post(
            "/api/v1/permission/check",
            json={
                "permission": "test_permission",
                "device_id": "test_device_001"
            }
        )
        
        # 应该返回认证错误
        assert response.status_code == 401
