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
