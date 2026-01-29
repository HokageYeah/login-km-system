"""
管理员服务层
提供管理后台相关的业务逻辑
"""
from typing import List, Tuple, Optional, Dict, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from loguru import logger

from app.models.user import User, UserStatus, UserRole
from app.models.card import Card, CardStatus
from app.models.card_device import CardDevice, CardDeviceStatus
from app.models.user_card import UserCard
from app.models.app import App
from app.utils.card_generator import generate_batch_cards


class AdminService:
    """管理员服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_cards(
        self,
        app_id: int,
        count: int,
        expire_time: datetime,
        max_device_count: int,
        permissions: Union[List[str], Dict],
        remark: Optional[str] = None
    ) -> Tuple[List[str], Optional[str]]:
        """
        批量生成卡密
        
        Args:
            app_id: 应用ID
            count: 生成数量
            expire_time: 过期时间
            max_device_count: 最大设备数
            permissions: 权限配置
            remark: 备注
            
        Returns:
            (卡密列表, 错误信息)
        """
        try:
            # 验证应用是否存在
            app = self.db.query(App).filter(App.id == app_id).first()
            if not app:
                return [], "应用不存在"
            
            if app.status != "normal":
                return [], "应用已禁用"
            
            # 生成卡密
            logger.info(f"开始生成 {count} 个卡密，应用ID: {app_id}")
            card_keys = generate_batch_cards(count, self.db)
            
            # 批量插入数据库
            cards_to_insert = []
            for card_key in card_keys:
                card = Card(
                    app_id=app_id,
                    card_key=card_key,
                    status=CardStatus.UNUSED,
                    expire_time=expire_time,
                    max_device_count=max_device_count,
                    permissions=permissions,
                    remark=remark
                )
                cards_to_insert.append(card)
            
            self.db.bulk_save_objects(cards_to_insert)
            self.db.commit()
            
            logger.info(f"成功生成 {len(card_keys)} 个卡密")
            return card_keys, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"生成卡密失败: {e}")
            return [], f"生成卡密失败: {str(e)}"
    
    def get_users_list(
        self,
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[Dict], int, Optional[str]]:
        """
        查询用户列表
        
        Args:
            page: 页码
            size: 每页数量
            status: 状态筛选
            keyword: 关键词搜索（用户名）
            
        Returns:
            (用户列表, 总数, 错误信息)
        """
        try:
            query = self.db.query(User)
            
            # 状态筛选
            if status:
                query = query.filter(User.status == status)
            
            # 关键词搜索
            if keyword:
                query = query.filter(User.username.like(f"%{keyword}%"))
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            users = query.order_by(User.created_at.desc()).offset((page - 1) * size).limit(size).all()
            
            # 统计每个用户的卡密数量
            user_list = []
            for user in users:
                # 查询用户绑定的有效卡密数量
                card_count = self.db.query(UserCard).filter(
                    UserCard.user_id == user.id,
                    UserCard.status == "active"
                ).count()
                
                user_list.append({
                    "id": user.id,
                    "username": user.username,
                    "status": user.status.value,
                    "role": user.role.value,
                    "card_count": card_count,
                    "created_at": user.created_at,
                    "last_login_at": user.last_login_at
                })
            
            return user_list, total, None
            
        except Exception as e:
            logger.error(f"查询用户列表失败: {e}")
            return [], 0, f"查询用户列表失败: {str(e)}"
    
    def update_user_status(
        self,
        user_id: int,
        status: str
    ) -> Tuple[bool, Optional[str]]:
        """
        更新用户状态
        
        Args:
            user_id: 用户ID
            status: 状态（normal/banned）
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在"
            
            # 验证状态值
            if status not in [UserStatus.NORMAL.value, UserStatus.BANNED.value]:
                return False, "无效的状态值"
            
            user.status = UserStatus(status)
            self.db.commit()
            
            logger.info(f"更新用户状态成功: user_id={user_id}, status={status}")
            return True, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户状态失败: {e}")
            return False, f"更新用户状态失败: {str(e)}"
    
    def get_cards_list(
        self,
        page: int = 1,
        size: int = 20,
        app_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[Dict], int, Optional[str]]:
        """
        查询卡密列表
        
        Args:
            page: 页码
            size: 每页数量
            app_id: 应用ID筛选
            status: 状态筛选
            keyword: 关键词搜索（卡密、备注）
            
        Returns:
            (卡密列表, 总数, 错误信息)
        """
        try:
            query = self.db.query(Card).join(App, Card.app_id == App.id)
            
            # 应用筛选
            if app_id:
                query = query.filter(Card.app_id == app_id)
            
            # 状态筛选
            if status:
                query = query.filter(Card.status == status)
            
            # 关键词搜索
            if keyword:
                query = query.filter(or_(
                    Card.card_key.like(f"%{keyword}%"),
                    Card.remark.like(f"%{keyword}%")
                ))
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            cards = query.order_by(Card.created_at.desc()).offset((page - 1) * size).limit(size).all()
            
            # 统计每个卡密的绑定信息
            card_list = []
            for card in cards:
                # 查询绑定的用户数量
                bind_user_count = self.db.query(UserCard).filter(
                    UserCard.card_id == card.id,
                    UserCard.status == "active"
                ).count()
                
                # 查询绑定的设备数量
                bind_device_count = self.db.query(CardDevice).filter(
                    CardDevice.card_id == card.id,
                    CardDevice.status == CardDeviceStatus.ACTIVE
                ).count()
                
                # 获取应用信息
                app = self.db.query(App).filter(App.id == card.app_id).first()
                
                card_list.append({
                    "id": card.id,
                    "app_id": card.app_id,
                    "app_name": app.app_name if app else "未知应用",
                    "card_key": card.card_key,
                    "status": card.status.value,
                    "expire_time": card.expire_time,
                    "max_device_count": card.max_device_count,
                    "permissions": card.permissions,
                    "remark": card.remark,
                    "bind_user_count": bind_user_count,
                    "bind_device_count": bind_device_count,
                    "created_at": card.created_at
                })
            
            return card_list, total, None
            
        except Exception as e:
            logger.error(f"查询卡密列表失败: {e}")
            return [], 0, f"查询卡密列表失败: {str(e)}"
    
    def update_card_status(
        self,
        card_id: int,
        status: str
    ) -> Tuple[bool, Optional[str]]:
        """
        更新卡密状态
        
        Args:
            card_id: 卡密ID
            status: 状态（unused/used/disabled）
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            card = self.db.query(Card).filter(Card.id == card_id).first()
            if not card:
                return False, "卡密不存在"
            
            # 验证状态值
            valid_statuses = [CardStatus.UNUSED.value, CardStatus.USED.value, CardStatus.DISABLED.value]
            if status not in valid_statuses:
                return False, "无效的状态值"
            
            card.status = CardStatus(status)
            self.db.commit()
            
            logger.info(f"更新卡密状态成功: card_id={card_id}, status={status}")
            return True, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新卡密状态失败: {e}")
            return False, f"更新卡密状态失败: {str(e)}"
    
    def update_card_permissions(
        self,
        card_id: int,
        permissions: Union[List[str], Dict]
    ) -> Tuple[bool, Optional[str]]:
        """
        更新卡密权限
        
        Args:
            card_id: 卡密ID
            permissions: 权限配置
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            card = self.db.query(Card).filter(Card.id == card_id).first()
            if not card:
                return False, "卡密不存在"
            
            old_permissions = card.permissions
            card.permissions = permissions
            self.db.commit()
            
            logger.info(f"更新卡密权限成功: card_id={card_id}, old={old_permissions}, new={permissions}")
            return True, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新卡密权限失败: {e}")
            return False, f"更新卡密权限失败: {str(e)}"
    
    def get_devices_list(
        self,
        page: int = 1,
        size: int = 20,
        card_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Dict], int, Optional[str]]:
        """
        查询设备列表
        
        Args:
            page: 页码
            size: 每页数量
            card_id: 卡密ID筛选
            user_id: 用户ID筛选
            status: 状态筛选
            
        Returns:
            (设备列表, 总数, 错误信息)
        """
        try:
            query = self.db.query(CardDevice).join(Card, CardDevice.card_id == Card.id)
            
            # 卡密筛选
            if card_id:
                query = query.filter(CardDevice.card_id == card_id)
            
            # 用户筛选
            if user_id:
                # 通过 UserCard 关联查询
                query = query.join(UserCard, UserCard.card_id == Card.id).filter(
                    UserCard.user_id == user_id,
                    UserCard.status == "active"
                )
            
            # 状态筛选
            if status:
                query = query.filter(CardDevice.status == status)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            devices = query.order_by(CardDevice.bind_time.desc()).offset((page - 1) * size).limit(size).all()
            
            # 构建返回数据
            device_list = []
            for device in devices:
                card = self.db.query(Card).filter(Card.id == device.card_id).first()
                
                device_list.append({
                    "id": device.id,
                    "card_id": device.card_id,
                    "card_key": card.card_key if card else "未知",
                    "device_id": device.device_id,
                    "device_name": device.device_name,
                    "bind_time": device.bind_time,
                    "last_active_at": device.last_active_at,
                    "status": device.status.value
                })
            
            return device_list, total, None
            
        except Exception as e:
            logger.error(f"查询设备列表失败: {e}")
            return [], 0, f"查询设备列表失败: {str(e)}"
    
    def update_device_status(
        self,
        device_id: int,
        status: str
    ) -> Tuple[bool, Optional[str]]:
        """
        更新设备状态
        
        Args:
            device_id: 设备绑定ID
            status: 状态（active/disabled）
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            device = self.db.query(CardDevice).filter(CardDevice.id == device_id).first()
            if not device:
                return False, "设备不存在"
            
            # 验证状态值
            valid_statuses = [CardDeviceStatus.ACTIVE.value, CardDeviceStatus.DISABLED.value]
            if status not in valid_statuses:
                return False, "无效的状态值"
            
            device.status = CardDeviceStatus(status)
            self.db.commit()
            
            logger.info(f"更新设备状态成功: device_id={device_id}, status={status}")
            return True, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新设备状态失败: {e}")
            return False, f"更新设备状态失败: {str(e)}"
    
    def get_statistics(self) -> Tuple[Dict, Optional[str]]:
        """
        获取统计数据
        
        Returns:
            (统计数据字典, 错误信息)
        """
        try:
            # 用户统计
            total_users = self.db.query(User).count()
            normal_users = self.db.query(User).filter(User.status == UserStatus.NORMAL).count()
            banned_users = self.db.query(User).filter(User.status == UserStatus.BANNED).count()
            
            # 卡密统计
            total_cards = self.db.query(Card).count()
            unused_cards = self.db.query(Card).filter(Card.status == CardStatus.UNUSED).count()
            used_cards = self.db.query(Card).filter(Card.status == CardStatus.USED).count()
            disabled_cards = self.db.query(Card).filter(Card.status == CardStatus.DISABLED).count()
            
            # 设备统计
            total_devices = self.db.query(CardDevice).count()
            active_devices = self.db.query(CardDevice).filter(CardDevice.status == CardDeviceStatus.ACTIVE).count()
            disabled_devices = self.db.query(CardDevice).filter(CardDevice.status == CardDeviceStatus.DISABLED).count()
            
            # 应用统计
            total_apps = self.db.query(App).count()
            active_apps = self.db.query(App).filter(App.status == "normal").count()
            
            statistics = {
                "users": {
                    "total": total_users,
                    "normal": normal_users,
                    "banned": banned_users
                },
                "cards": {
                    "total": total_cards,
                    "unused": unused_cards,
                    "used": used_cards,
                    "disabled": disabled_cards
                },
                "devices": {
                    "total": total_devices,
                    "active": active_devices,
                    "disabled": disabled_devices
                },
                "apps": {
                    "total": total_apps,
                    "active": active_apps
                }
            }
            
            return statistics, None
            
        except Exception as e:
            logger.error(f"获取统计数据失败: {e}")
            return {}, f"获取统计数据失败: {str(e)}"
