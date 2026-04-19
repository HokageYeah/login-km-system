"""
卡密服务层
处理卡密相关的业务逻辑
"""
from datetime import datetime
from typing import Optional, Tuple, List, Dict
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

    @staticmethod
    def _is_card_expired(card: Card) -> bool:
        """按过期时间动态判断卡密是否已过期，不写回数据库状态。"""
        return bool(card.expire_time and card.expire_time < datetime.now())

    def _get_active_device_ids_by_card_ids(self, card_ids: List[int]) -> Dict[int, List[str]]:
        """
        批量查询卡密绑定的活跃设备ID列表。

        这里按卡密ID批量查，而不是在循环中逐个查设备列表，避免用户绑定多张卡密时产生额外的 N+1 查询。
        """
        if not card_ids:
            return {}

        device_rows = self.db.query(
            CardDevice.card_id,
            CardDevice.device_id
        ).filter(
            and_(
                CardDevice.card_id.in_(card_ids),
                CardDevice.status == CardDeviceStatus.ACTIVE
            )
        ).order_by(CardDevice.bind_time.asc()).all()

        devices_map: Dict[int, List[str]] = {card_id: [] for card_id in card_ids}
        for card_id, device_id in device_rows:
            devices_map.setdefault(card_id, []).append(device_id)

        return devices_map
    
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
        
        card_ids = [card.id for _, card, _ in user_cards]
        devices_map = self._get_active_device_ids_by_card_ids(card_ids)

        result = []
        for user_card, card, app in user_cards:
            # 设备ID列表与已绑定设备数量使用同一份查询结果，避免数量和列表来源不一致。
            device_ids = devices_map.get(card.id, [])
            
            result.append({
                "card_id": card.id,
                "card_key": card.card_key,
                "app_name": app.app_name,
                "app_id": app.id,
                "app_key": app.app_key,
                "app_status": app.status,
                "app_created_at": app.created_at,
                "expire_time": card.expire_time,
                "is_expired": self._is_card_expired(card),
                "permissions": card.permissions,
                "bind_devices": len(device_ids),
                "devices": device_ids,
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

        app = self.db.query(App).filter(App.id == card.app_id).first()
        if not app:
            return None, "卡密所属应用不存在"
        
        # 3. 验证卡密状态
        if card.status == CardStatus.DISABLED:
            return None, "卡密已被禁用"
        
        # 4. 验证卡密是否过期
        if self._is_card_expired(card):
            return None, "卡密已过期"
        
        # 5. 检查用户是否曾绑定该卡密
        # user_cards 在数据库层限制同一用户和卡密只能有一条记录；
        # 解绑后再次绑定应恢复历史记录，而不是插入新记录导致唯一索引冲突。
        existing_binding = self.db.query(UserCard).filter(
            and_(
                UserCard.user_id == user_id,
                UserCard.card_id == card.id
            )
        ).first()

        # 6. 检查设备是否已绑定该卡密
        # card_devices 同样有唯一索引，必须统一处理已有记录，避免重复插入。
        existing_device = self.db.query(CardDevice).filter(
            and_(
                CardDevice.card_id == card.id,
                CardDevice.device_id == device_id
            )
        ).first()

        if existing_device:
            if existing_device.status == CardDeviceStatus.DISABLED:
                return None, "该设备已被禁用"
            if not existing_binding:
                return None, "该设备已绑定此卡密"
            if existing_binding and existing_binding.status == UserCardStatus.ACTIVE:
                return None, "该设备已绑定此卡密"
        
        if not existing_device:
            # 7. 检查设备数量限制
            active_devices = self.db.query(CardDevice).filter(
                and_(
                    CardDevice.card_id == card.id,
                    CardDevice.status == CardDeviceStatus.ACTIVE
                )
            ).count()
            
            if active_devices >= card.max_device_count:
                return None, f"设备数量已达上限（{card.max_device_count}个）"
        
        now = datetime.now()

        # 8. 创建或恢复用户-卡密绑定
        if existing_binding:
            if existing_binding.status != UserCardStatus.ACTIVE:
                existing_binding.status = UserCardStatus.ACTIVE
                existing_binding.bind_time = now
        else:
            user_card = UserCard(
                user_id=user_id,
                card_id=card.id,
                bind_time=now,
                status=UserCardStatus.ACTIVE
            )
            self.db.add(user_card)
        
        # 9. 创建或更新设备绑定
        if existing_device:
            existing_device.device_name = device_name or existing_device.device_name
            existing_device.last_active_at = now
        else:
            card_device = CardDevice(
                card_id=card.id,
                device_id=device_id,
                device_name=device_name,
                bind_time=now,
                last_active_at=now,
                status=CardDeviceStatus.ACTIVE
            )
            self.db.add(card_device)
        
        # 10. 更新卡密状态为已使用
        if card.status == CardStatus.UNUSED:
            card.status = CardStatus.USED
        
        self.db.commit()
        
        logger.info(f"用户 {user_id} 成功绑定卡密 {card_key}，设备: {device_id}")
        
        # 11. 返回卡密信息
        return {
            "card_id": card.id,
            "card_key": card.card_key,
            "expire_time": card.expire_time,
            "permissions": card.permissions,
            "max_device_count": card.max_device_count,
            "remark": card.remark,
            "app_name": app.app_name,
            "app_id": app.id,
            "app_key": app.app_key,
            "app_status": app.status.value,
            "app_created_at": app.created_at
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
            if self._is_card_expired(card):
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
    
    def batch_delete_cards(self, card_ids: List[int]) -> Tuple[int, List[int], Optional[str]]:
        """
        批量删除卡密
        
        Args:
            card_ids: 要删除的卡密ID列表
            
        Returns:
            (成功删除数量, 失败的ID列表, 错误信息)
        """
        if not card_ids:
            return 0, [], "卡密ID列表不能为空"
        
        deleted_count = 0
        failed_ids = []
        
        for card_id in card_ids:
            try:
                # 查询卡密是否存在
                card = self.db.query(Card).filter(Card.id == card_id).first()
                if not card:
                    logger.warning(f"卡密不存在，跳过删除: ID {card_id}")
                    failed_ids.append(card_id)
                    continue
                
                # 先删除卡密的设备绑定（避免外键约束问题）
                self.db.query(CardDevice).filter(CardDevice.card_id == card_id).delete()
                
                # 删除卡密的用户绑定
                self.db.query(UserCard).filter(UserCard.card_id == card_id).delete()
                
                # 最后删除卡密
                self.db.delete(card)
                self.db.commit()
                
                deleted_count += 1
                logger.info(f"成功删除卡密: {card.card_key} (ID: {card_id})")
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"删除卡密失败: ID {card_id}, 错误: {str(e)}")
                failed_ids.append(card_id)
        
        return deleted_count, failed_ids, None


def get_card_service(db: Session) -> CardService:
    """
    获取卡密服务实例
    
    Args:
        db: 数据库会话
        
    Returns:
        CardService实例
    """
    return CardService(db)
