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

    def test_admin_permission_check_without_card(self, db_session, test_admin):
        """测试管理员无卡密时也能通过权限校验"""
        from app.services.permission_service import PermissionService

        permission_service = PermissionService(db_session)

        allowed, message, expire_time = permission_service.check_permission(
            user_id=test_admin.id,
            device_id="admin_device_001",
            permission="test_permission"
        )

        assert allowed is True
        assert "管理员" in message
        assert expire_time is None

    def test_admin_get_permissions_without_card(self, db_session, test_admin):
        """测试管理员无卡密时可获取全部正常权限"""
        from app.services.permission_service import PermissionService
        from app.models.feature_permission import FeaturePermission, FeaturePermissionStatus

        db_session.add_all([
            FeaturePermission(
                permission_key="wechat",
                permission_name="微信抓取",
                status=FeaturePermissionStatus.NORMAL.value,
                sort_order=2
            ),
            FeaturePermission(
                permission_key="ximalaya",
                permission_name="喜马拉雅",
                status=FeaturePermissionStatus.NORMAL.value,
                sort_order=1
            ),
            FeaturePermission(
                permission_key="disabled_permission",
                permission_name="已禁用权限",
                status=FeaturePermissionStatus.DISABLED.value,
                sort_order=3
            )
        ])
        db_session.commit()

        permission_service = PermissionService(db_session)

        has_permission, permissions, expire_time = permission_service.get_user_permissions(
            user_id=test_admin.id,
            device_id="admin_device_001"
        )

        assert has_permission is True
        assert permissions == ["ximalaya", "wechat"]
        assert expire_time is None

    def test_current_card_permission_scope(self, db_session, test_user, test_app):
        """测试当前卡密权限不会串用同设备其他卡密权限"""
        from app.services.permission_service import PermissionService
        from app.models.card import Card, CardStatus
        from app.models.user_card import UserCard, UserCardStatus
        from app.models.card_device import CardDevice, CardDeviceStatus

        card_wechat = Card(
            app_id=test_app.id,
            card_key="TEST-WECHAT-CARD-123",
            status=CardStatus.USED,
            expire_time=datetime.now() + timedelta(days=30),
            max_device_count=2,
            permissions=["wechatpublic"]
        )
        card_ximalaya = Card(
            app_id=test_app.id,
            card_key="TEST-XIMALAYA-CARD",
            status=CardStatus.USED,
            expire_time=datetime.now() + timedelta(days=30),
            max_device_count=2,
            permissions=["ximalaya"]
        )
        db_session.add_all([card_wechat, card_ximalaya])
        db_session.commit()
        db_session.refresh(card_wechat)
        db_session.refresh(card_ximalaya)

        now = datetime.now()
        db_session.add_all([
            UserCard(
                user_id=test_user.id,
                card_id=card_wechat.id,
                bind_time=now,
                status=UserCardStatus.ACTIVE
            ),
            UserCard(
                user_id=test_user.id,
                card_id=card_ximalaya.id,
                bind_time=now,
                status=UserCardStatus.ACTIVE
            ),
            CardDevice(
                card_id=card_wechat.id,
                device_id="test_device_001",
                bind_time=now,
                status=CardDeviceStatus.ACTIVE
            ),
            CardDevice(
                card_id=card_ximalaya.id,
                device_id="test_device_001",
                bind_time=now,
                status=CardDeviceStatus.ACTIVE
            )
        ])
        db_session.commit()

        permission_service = PermissionService(db_session)

        allowed, message, expire_time = permission_service.check_permission(
            user_id=test_user.id,
            device_id="test_device_001",
            permission="ximalaya",
            card_id=card_wechat.id
        )
        assert allowed is False
        assert message == "当前卡密没有该系统权限，请切换卡密或联系管理员开通权限"
        assert expire_time is None

        has_permission, permissions, expire_time = permission_service.get_user_permissions(
            user_id=test_user.id,
            device_id="test_device_001",
            card_id=card_wechat.id
        )
        assert has_permission is True
        assert permissions == ["wechatpublic"]

        allowed, message, expire_time = permission_service.check_permission(
            user_id=test_user.id,
            device_id="test_device_001",
            permission="ximalaya"
        )
        assert allowed is True

        has_permission, permissions, expire_time = permission_service.get_user_permissions(
            user_id=test_user.id,
            device_id="test_device_001"
        )
        assert has_permission is True
        assert permissions == ["wechatpublic", "ximalaya"]

    def test_get_user_permissions_returns_check_permission_message_for_unbound_card(
        self,
        db_session,
        test_user,
        test_app
    ):
        """测试查询当前卡密权限时，失败原因直接复用 check_permission 的统一文案"""
        from app.services.permission_service import PermissionService
        from app.models.card import Card, CardStatus

        card = Card(
            app_id=test_app.id,
            card_key="TEST-UNBOUND-CARD-1234",
            status=CardStatus.USED,
            expire_time=datetime.now() + timedelta(days=30),
            max_device_count=2,
            permissions=["wechat"]
        )
        db_session.add(card)
        db_session.commit()
        db_session.refresh(card)

        permission_service = PermissionService(db_session)

        has_permission, permissions, expire_time, message = permission_service.get_user_permissions_with_message(
            user_id=test_user.id,
            device_id="test_device_001",
            card_id=card.id
        )

        assert has_permission is False
        assert permissions == []
        assert expire_time is None
        assert message == "当前用户未绑定指定卡密"


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
