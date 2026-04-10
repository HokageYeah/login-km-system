"""
卡密模块测试
"""
import pytest
from datetime import datetime, timedelta


class TestCardGenerator:
    """卡密生成器测试"""
    
    def test_generate_single_card(self):
        """测试生成单个卡密"""
        from app.utils.card_generator import generate_card_key, validate_card_key_format
        
        card_key = generate_card_key()
        
        # 验证格式
        assert card_key is not None
        assert len(card_key) == 19  # XXXX-XXXX-XXXX-XXXX
        assert card_key.count('-') == 3
        assert validate_card_key_format(card_key)
    
    def test_generate_batch_cards(self):
        """测试批量生成卡密"""
        from app.utils.card_generator import generate_batch_cards
        
        count = 100
        cards = generate_batch_cards(count)
        
        # 验证数量
        assert len(cards) == count
        
        # 验证唯一性
        assert len(set(cards)) == count
    
    def test_validate_card_format(self):
        """测试卡密格式验证"""
        from app.utils.card_generator import validate_card_key_format
        
        # 有效格式
        assert validate_card_key_format("A3KD-Q7LM-P2E8-W9RZ")
        assert validate_card_key_format("ABCD-EFGH-JKLM-NPQR")
        
        # 无效格式
        assert not validate_card_key_format("ABCD-EFGH-JKLM")  # 太短
        assert not validate_card_key_format("A0CD-EFGH-JKLM-NPQR")  # 包含0
        assert not validate_card_key_format("AICD-EFGH-JKLM-NPQR")  # 包含I
        assert not validate_card_key_format("ABCD-EFGH-JKLM-NPQR-STUV")  # 太长
    
    def test_normalize_card_key(self):
        """测试卡密规范化"""
        from app.utils.card_generator import normalize_card_key
        
        # 小写转大写
        assert normalize_card_key("abcd-efgh-jklm-npqr") == "ABCD-EFGH-JKLM-NPQR"
        
        # 无分隔符
        assert normalize_card_key("ABCDEFGHJKLMNPQR") == "ABCD-EFGH-JKLM-NPQR"
        
        # 混合
        assert normalize_card_key("abcdefghjklmnpqr") == "ABCD-EFGH-JKLM-NPQR"


class TestCardAPI:
    """卡密API测试"""
    
    def test_bind_card_without_login(self, client):
        """测试未登录绑定卡密"""
        response = client.post(
            "/api/v1/card/bind",
            json={
                "card_key": "TEST-CARD-KEY1-2345",
                "device_id": "test_device_001"
            }
        )
        
        # 应该返回认证错误
        assert response.status_code == 401
    
    def test_query_my_cards_without_login(self, client):
        """测试未登录查询我的卡密"""
        response = client.get("/api/v1/card/my")
        
        # 应该返回认证错误
        assert response.status_code == 401


@pytest.mark.asyncio
class TestCardService:
    """CardService 测试"""
    
    def test_card_binding_logic(self, db_session, test_user, test_app):
        """测试卡密绑定逻辑"""
        from app.services.card_service import CardService
        from app.models.card import Card, CardStatus
        from datetime import datetime, timedelta
        
        # 创建测试卡密
        card = Card(
            app_id=test_app.id,
            card_key="TEST-CARD-KEY1-2345",
            status=CardStatus.UNUSED,
            expire_time=datetime.now() + timedelta(days=30),
            max_device_count=2,
            permissions=["test_permission"]
        )
        db_session.add(card)
        db_session.commit()
        db_session.refresh(card)
        
        # 测试绑定
        card_service = CardService(db_session)
        result, error = card_service.bind_card(
            user_id=test_user.id,
            card_key="TEST-CARD-KEY1-2345",
            app_id=test_app.id,
            device_id="test_device_001"
        )
        
        # 验证绑定成功
        assert error is None
        assert result is not None
        assert result["app_name"] == test_app.app_name
        assert result["app_id"] == test_app.id
        assert result["app_key"] == test_app.app_key

    def test_get_user_cards_returns_is_expired_flag(self, db_session):
        """测试查询我的卡密时返回动态过期标记且不改原状态"""
        from app.services.card_service import CardService
        from app.models.card import Card, CardStatus
        from app.models.user_card import UserCard, UserCardStatus
        from app.models.app import App, AppStatus
        from app.models.user import User, UserStatus, UserRole
        from app.utils.security import hash_password

        app = App(
            app_key="expired_flag_app",
            app_name="过期状态测试应用",
            status=AppStatus.NORMAL
        )
        user = User(
            username="expired_flag_user",
            password_hash=hash_password("testpass123"),
            status=UserStatus.NORMAL,
            role=UserRole.USER
        )
        db_session.add_all([app, user])
        db_session.commit()
        db_session.refresh(app)
        db_session.refresh(user)

        expired_card = Card(
            app_id=app.id,
            card_key="EXPD-CARD-KEY1-2345",
            status=CardStatus.USED,
            expire_time=datetime.now() - timedelta(days=1),
            max_device_count=1,
            permissions=["test_permission"]
        )
        db_session.add(expired_card)
        db_session.commit()
        db_session.refresh(expired_card)

        user_card = UserCard(
            user_id=user.id,
            card_id=expired_card.id,
            bind_time=datetime.now() - timedelta(days=2),
            status=UserCardStatus.ACTIVE
        )
        db_session.add(user_card)
        db_session.commit()

        card_service = CardService(db_session)
        cards = card_service.get_user_cards(user.id)

        assert len(cards) == 1
        assert cards[0]["status"] == CardStatus.USED.value
        assert cards[0]["is_expired"] is True

    def test_bind_card_reactivates_unbound_user_card(self, db_session):
        """测试解绑后重绑复用历史用户卡密记录，避免唯一索引冲突"""
        from app.services.card_service import CardService
        from app.models.app import App, AppStatus
        from app.models.user import User, UserStatus, UserRole
        from app.models.card import Card, CardStatus
        from app.models.user_card import UserCard, UserCardStatus
        from app.models.card_device import CardDevice
        from app.utils.security import hash_password

        app = App(
            app_key="rebind_app",
            app_name="重绑测试应用",
            status=AppStatus.NORMAL
        )
        user = User(
            username="rebind_user",
            password_hash=hash_password("testpass123"),
            status=UserStatus.NORMAL,
            role=UserRole.USER
        )
        db_session.add_all([app, user])
        db_session.commit()
        db_session.refresh(app)
        db_session.refresh(user)

        card = Card(
            app_id=app.id,
            card_key="RBND-CARD-KEY1-2345",
            status=CardStatus.USED,
            expire_time=datetime.now() + timedelta(days=30),
            max_device_count=1,
            permissions=["test_permission"]
        )
        db_session.add(card)
        db_session.commit()
        db_session.refresh(card)

        user_card = UserCard(
            user_id=user.id,
            card_id=card.id,
            bind_time=datetime.now() - timedelta(days=2),
            status=UserCardStatus.UNBIND
        )
        db_session.add(user_card)
        db_session.commit()

        card_service = CardService(db_session)
        result, error = card_service.bind_card(
            user_id=user.id,
            card_key=card.card_key,
            app_id=app.id,
            device_id="rebind_device_001",
            device_name="重绑设备"
        )

        db_session.refresh(user_card)
        user_card_count = db_session.query(UserCard).filter(
            UserCard.user_id == user.id,
            UserCard.card_id == card.id
        ).count()
        device_count = db_session.query(CardDevice).filter(
            CardDevice.card_id == card.id,
            CardDevice.device_id == "rebind_device_001"
        ).count()

        assert error is None
        assert result is not None
        assert result["app_name"] == app.app_name
        assert result["app_id"] == app.id
        assert result["app_key"] == app.app_key
        assert user_card.status == UserCardStatus.ACTIVE
        assert user_card_count == 1
        assert device_count == 1
