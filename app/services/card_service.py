"""
卡密服务层
处理卡密相关的业务逻辑
"""
from datetime import datetime
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.card import Card, CardStatus
from app.models.user_card import UserCard, UserCardStatus
from app.models.card_device import CardDevice, CardDeviceStatus
from app.models.app import App, AppStatus
from app.core.logging_uru import logger


class CardService:
    """卡密服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_cards(self, user_id: int) -> List[dict]:
        """
        查询用户的所有卡密
        
        Args:
            user_id: 用户ID
            
        Returns:
            卡密信息列表
        """
        # 查询用户绑定的卡密
        user_cards = self.db.query(UserCard, Card, App).join(
            Card, UserCard.card_id == Card.id
        ).join(
            App, Card.app_id == App.id
        ).filter(
            and_(
                UserCard.user_id == user_id,
                UserCard.status == UserCardStatus.ACTIVE
            )
        ).all()
        
        result = []
        for user_card, card, app in user_cards:
            # 统计已绑定设备数
            device_count = self.db.query(CardDevice).filter(
                and_(
                    CardDevice.card_id == card.id,
                    CardDevice.status == CardDeviceStatus.ACTIVE
                )
            ).count()
            
            result.append({
                "card_id": card.id,
                "card_key": card.card_key,
                "app_name": app.app_name,
                "expire_time": card.expire_time,
                "permissions": card.permissions,
                "bind_devices": device_count,
                "max_device_count": card.max_device_count,
                "status": card.status.value,
                "remark": card.remark
            })
        
        return result
    
    def bind_card(
        self,
        user_id: int,
        card_key: str,
        app_id: int,
        device_id: str,
        device_name: Optional[str] = None
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        绑定卡密
        
        Args:
            user_id: 用户ID
            card_key: 卡密字符串
            app_id: 应用ID
            device_id: 设备ID
            device_name: 设备名称（可选）
            
        Returns:
            (卡密信息, 错误信息)
        """
        # 1. 查询卡密
        card = self.db.query(Card).filter(Card.card_key == card_key).first()
        if not card:
            return None, "卡密不存在"
        
        # 2. 验证卡密是否属于当前应用
        if card.app_id != app_id:
            return None, "卡密不属于当前应用"
        
        # 3. 验证卡密状态
        if card.status == CardStatus.DISABLED:
            return None, "卡密已被禁用"
        
        # 4. 验证卡密是否过期
        if card.expire_time < datetime.now():
            return None, "卡密已过期"
        
        # 5. 检查用户是否已绑定该卡密
        existing_binding = self.db.query(UserCard).filter(
            and_(
                UserCard.user_id == user_id,
                UserCard.card_id == card.id,
                UserCard.status == UserCardStatus.ACTIVE
            )
        ).first()
        
        if existing_binding:
            # 用户已绑定该卡密，检查设备是否已绑定
            existing_device = self.db.query(CardDevice).filter(
                and_(
                    CardDevice.card_id == card.id,
                    CardDevice.device_id == device_id
                )
            ).first()
            
            if existing_device:
                if existing_device.status == CardDeviceStatus.DISABLED:
                    return None, "该设备已被禁用"
                return None, "该设备已绑定此卡密"
        
        # 6. 检查设备数量限制
        active_devices = self.db.query(CardDevice).filter(
            and_(
                CardDevice.card_id == card.id,
                CardDevice.status == CardDeviceStatus.ACTIVE
            )
        ).count()
        
        if active_devices >= card.max_device_count:
            return None, f"设备数量已达上限（{card.max_device_count}个）"
        
        # 7. 创建用户-卡密绑定（如果不存在）
        if not existing_binding:
            user_card = UserCard(
                user_id=user_id,
                card_id=card.id,
                bind_time=datetime.now(),
                status=UserCardStatus.ACTIVE
            )
            self.db.add(user_card)
        
        # 8. 创建设备绑定
        card_device = CardDevice(
            card_id=card.id,
            device_id=device_id,
            device_name=device_name,
            bind_time=datetime.now(),
            last_active_at=datetime.now(),
            status=CardDeviceStatus.ACTIVE
        )
        self.db.add(card_device)
        
        # 9. 更新卡密状态为已使用
        if card.status == CardStatus.UNUSED:
            card.status = CardStatus.USED
        
        self.db.commit()
        
        logger.info(f"用户 {user_id} 成功绑定卡密 {card_key}，设备: {device_id}")
        
        # 10. 返回卡密信息
        return {
            "card_id": card.id,
            "card_key": card.card_key,
            "expire_time": card.expire_time,
            "permissions": card.permissions,
            "max_device_count": card.max_device_count,
            "remark": card.remark
        }, None
    
    def unbind_device(
        self,
        user_id: int,
        card_id: int,
        device_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        解绑设备
        
        Args:
            user_id: 用户ID
            card_id: 卡密ID
            device_id: 设备ID
            
        Returns:
            (是否成功, 错误信息)
        """
        # 1. 验证用户是否拥有该卡密
        user_card = self.db.query(UserCard).filter(
            and_(
                UserCard.user_id == user_id,
                UserCard.card_id == card_id,
                UserCard.status == UserCardStatus.ACTIVE
            )
        ).first()
        
        if not user_card:
            return False, "您没有绑定该卡密"
        
        # 2. 查找设备绑定
        device_binding = self.db.query(CardDevice).filter(
            and_(
                CardDevice.card_id == card_id,
                CardDevice.device_id == device_id
            )
        ).first()
        
        if not device_binding:
            return False, "设备绑定不存在"
        
        # 3. 删除设备绑定
        self.db.delete(device_binding)
        
        # 4. 检查该卡密是否还有其他活跃设备
        remaining_devices = self.db.query(CardDevice).filter(
            and_(
                CardDevice.card_id == card_id,
                CardDevice.status == CardDeviceStatus.ACTIVE,
                CardDevice.device_id != device_id
            )
        ).count()
        
        # 5. 如果没有其他设备，解绑用户-卡密关系
        if remaining_devices == 0:
            user_card.status = UserCardStatus.UNBIND
            
            # 检查是否还有其他用户绑定此卡密
            other_users = self.db.query(UserCard).filter(
                and_(
                    UserCard.card_id == card_id,
                    UserCard.status == UserCardStatus.ACTIVE,
                    UserCard.user_id != user_id
                )
            ).count()
            
            # 如果没有其他用户，将卡密状态改回未使用
            if other_users == 0:
                card = self.db.query(Card).filter(Card.id == card_id).first()
                if card:
                    card.status = CardStatus.UNUSED
        
        self.db.commit()
        
        logger.info(f"用户 {user_id} 解绑设备 {device_id} from 卡密 {card_id}")
        
        return True, None
    
    def get_card_detail(self, card_id: int) -> Optional[dict]:
        """
        获取卡密详情
        
        Args:
            card_id: 卡密ID
            
        Returns:
            卡密详情
        """
        # 查询卡密
        card = self.db.query(Card, App).join(
            App, Card.app_id == App.id
        ).filter(Card.id == card_id).first()
        
        if not card:
            return None
        
        card_obj, app = card
        
        # 查询绑定的设备
        devices = self.db.query(CardDevice).filter(
            CardDevice.card_id == card_id
        ).all()
        
        device_list = [{
            "device_id": device.device_id,
            "device_name": device.device_name,
            "bind_time": device.bind_time,
            "last_active_at": device.last_active_at,
            "status": device.status.value
        } for device in devices]
        
        return {
            "card_id": card_obj.id,
            "card_key": card_obj.card_key,
            "app_name": app.app_name,
            "status": card_obj.status.value,
            "expire_time": card_obj.expire_time,
            "max_device_count": card_obj.max_device_count,
            "permissions": card_obj.permissions,
            "remark": card_obj.remark,
            "devices": device_list,
            "created_at": card_obj.created_at
        }
    
    def check_card_available(
        self,
        user_id: int,
        device_id: str
    ) -> Tuple[Optional[Card], Optional[str]]:
        """
        检查用户在指定设备上是否有可用的卡密
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            
        Returns:
            (卡密对象, 错误信息)
        """
        # 查询用户的活跃卡密
        user_cards = self.db.query(UserCard, Card).join(
            Card, UserCard.card_id == Card.id
        ).filter(
            and_(
                UserCard.user_id == user_id,
                UserCard.status == UserCardStatus.ACTIVE
            )
        ).all()
        
        if not user_cards:
            return None, "未绑定卡密"
        
        # 检查每个卡密
        for user_card, card in user_cards:
            # 检查卡密状态
            if card.status == CardStatus.DISABLED:
                continue
            
            # 检查是否过期
            if card.expire_time < datetime.now():
                continue
            
            # 检查设备是否绑定
            device_binding = self.db.query(CardDevice).filter(
                and_(
                    CardDevice.card_id == card.id,
                    CardDevice.device_id == device_id,
                    CardDevice.status == CardDeviceStatus.ACTIVE
                )
            ).first()
            
            if device_binding:
                # 更新设备最后活跃时间
                device_binding.last_active_at = datetime.now()
                self.db.commit()
                return card, None
        
        return None, "该设备未绑定有效卡密"


def get_card_service(db: Session) -> CardService:
    """
    获取卡密服务实例
    
    Args:
        db: 数据库会话
        
    Returns:
        CardService实例
    """
    return CardService(db)
