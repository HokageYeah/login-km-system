"""
管理员服务层
提供管理后台相关的业务逻辑
"""
from typing import List, Tuple, Optional, Dict, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from loguru import logger

from app.models.user import User, UserStatus, UserRole
from app.models.card import Card, CardStatus
from app.models.card_device import CardDevice, CardDeviceStatus
from app.models.user_card import UserCard, UserCardStatus
from app.models.app import App
from app.utils.card_generator import generate_batch_cards


class AdminService:
    """管理员服务类"""
    
    def __init__(self, db: Session):
        self.db = db

    def _build_recent_creation_trend(
        self,
        model,
        days: int = 7,
        field_name: str = "created_at"
    ) -> Dict[str, List[int] | List[str]]:
        """
        构建最近 N 天的新增与累计趋势

        这里统一基于 created_at 统计，确保仪表盘展示的“每日新增”与“累计规模”
        都来自真实数据，而不是前端模拟值。
        """
        date_field = getattr(model, field_name)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date + timedelta(days=1), datetime.min.time())

        daily_rows = (
            self.db.query(
                func.date(date_field).label("day"),
                func.count(model.id).label("count")
            )
            .filter(date_field >= start_datetime, date_field < end_datetime)
            .group_by(func.date(date_field))
            .all()
        )

        counts_by_day: Dict[str, int] = {}
        for row in daily_rows:
            day_value = row.day
            day_key = day_value if isinstance(day_value, str) else day_value.isoformat()
            counts_by_day[day_key] = int(row.count)

        base_total = (
            self.db.query(func.count(model.id))
            .filter(date_field < start_datetime)
            .scalar()
            or 0
        )

        labels: List[str] = []
        daily_counts: List[int] = []
        cumulative_counts: List[int] = []
        running_total = int(base_total)

        for offset in range(days):
            current_date = start_date + timedelta(days=offset)
            current_key = current_date.isoformat()
            current_count = counts_by_day.get(current_key, 0)

            labels.append(current_date.strftime("%m-%d"))
            daily_counts.append(current_count)

            running_total += current_count
            cumulative_counts.append(running_total)

        return {
            "labels": labels,
            "daily": daily_counts,
            "cumulative": cumulative_counts
        }

    def _sync_card_usage_statuses(self, card_ids: Optional[List[int]] = None) -> bool:
        """
        根据有效用户绑定关系同步卡密 used/unused 状态。

        disabled 是管理员显式禁用状态，不参与自动同步；其他状态以 user_cards
        的 active 绑定事实为准，避免过期时间调整、禁用后启用等入口造成状态漂移。
        """
        if card_ids is not None:
            card_ids = list(set(card_ids))
            if not card_ids:
                return False

        active_binding_query = self.db.query(UserCard.card_id).filter(
            UserCard.status == UserCardStatus.ACTIVE
        )
        card_query = self.db.query(Card).filter(Card.status != CardStatus.DISABLED)

        if card_ids is not None:
            active_binding_query = active_binding_query.filter(UserCard.card_id.in_(card_ids))
            card_query = card_query.filter(Card.id.in_(card_ids))

        active_card_ids = {
            row.card_id for row in active_binding_query.distinct().all()
        }

        changed = False
        for card in card_query.all():
            expected_status = CardStatus.USED if card.id in active_card_ids else CardStatus.UNUSED
            if card.status != expected_status:
                card.status = expected_status
                changed = True

        if changed:
            self.db.flush()

        return changed
    
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

    def get_user_active_cards(
        self,
        user_id: int
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        查询用户当前有效卡密详情

        Args:
            user_id: 用户ID

        Returns:
            (用户有效卡密详情, 错误信息)
        """
        try:
            now = datetime.now()
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None, "用户不存在"

            # 用户列表中的“有效卡密”当前表示有效绑定关系，这里必须保持同一口径，
            # 避免列表有数量但详情弹窗为空；卡密是否过期/禁用通过明细字段展示。
            user_cards = self.db.query(UserCard, Card, App).join(
                Card, UserCard.card_id == Card.id
            ).join(
                App, Card.app_id == App.id
            ).filter(
                UserCard.user_id == user_id,
                UserCard.status == "active"
            ).order_by(UserCard.bind_time.desc()).all()

            if not user_cards:
                return {
                    "user_id": user.id,
                    "username": user.username,
                    "total": 0,
                    "cards": []
                }, None

            card_ids = [card.id for _, card, _ in user_cards]
            if self._sync_card_usage_statuses(card_ids):
                self.db.commit()
            active_device_rows = self.db.query(
                CardDevice.card_id,
                func.count(CardDevice.id)
            ).filter(
                CardDevice.card_id.in_(card_ids),
                CardDevice.status == CardDeviceStatus.ACTIVE
            ).group_by(CardDevice.card_id).all()
            bind_device_count_map = {card_id: count for card_id, count in active_device_rows}

            cards = []
            for user_card, card, app in user_cards:
                cards.append({
                    "card_id": card.id,
                    "card_key": card.card_key,
                    "app_id": app.id,
                    "app_name": app.app_name,
                    "status": card.status.value,
                    "is_expired": bool(card.expire_time and card.expire_time < now),
                    "expire_time": card.expire_time,
                    "max_device_count": card.max_device_count,
                    "bind_device_count": bind_device_count_map.get(card.id, 0),
                    "permissions": card.permissions,
                    "remark": card.remark,
                    "bind_time": user_card.bind_time
                })

            return {
                "user_id": user.id,
                "username": user.username,
                "total": len(cards),
                "cards": cards
            }, None

        except Exception as e:
            logger.error(f"查询用户有效卡密详情失败: user_id={user_id}, error={e}")
            return None, f"查询用户有效卡密详情失败: {str(e)}"
    
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
        keyword: Optional[str] = None,
        username: Optional[str] = None
    ) -> Tuple[List[Dict], int, Optional[str]]:
        """
        查询卡密列表
        
        Args:
            page: 页码
            size: 每页数量
            app_id: 应用ID筛选
            status: 状态筛选
            keyword: 关键词搜索（卡密、备注）
            username: 用户名筛选
            
        Returns:
            (卡密列表, 总数, 错误信息)
        """
        try:
            now = datetime.now()
            if self._sync_card_usage_statuses():
                self.db.commit()

            query = self.db.query(Card).join(App, Card.app_id == App.id)
            
            # 应用筛选
            if app_id:
                query = query.filter(Card.app_id == app_id)
            
            # 状态筛选
            # expired 是管理端专用的时间维度筛选，不写入数据库状态枚举。
            # 选择 expired 时，不关心 unused/used/disabled，只筛选所有已过期卡密。
            if status:
                if status == "expired":
                    query = query.filter(Card.expire_time < now)
                else:
                    query = query.filter(Card.status == status)
            
            # 关键词搜索
            if keyword:
                query = query.filter(or_(
                    Card.card_key.like(f"%{keyword}%"),
                    Card.remark.like(f"%{keyword}%")
                ))

            if username:
                username_card_subquery = self.db.query(UserCard.card_id).join(
                    User, User.id == UserCard.user_id
                ).filter(
                    UserCard.status == "active",
                    User.username.ilike(f"%{username.strip()}%")
                )
                query = query.filter(Card.id.in_(username_card_subquery))
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            cards = query.order_by(Card.created_at.desc()).offset((page - 1) * size).limit(size).all()
            
            if not cards:
                return [], total, None

            card_ids = [card.id for card in cards]

            user_bindings = self.db.query(
                UserCard.card_id,
                User.username
            ).join(User, User.id == UserCard.user_id).filter(
                UserCard.card_id.in_(card_ids),
                UserCard.status == "active"
            ).all()

            card_usernames_map: Dict[int, List[str]] = {}
            for binding in user_bindings:
                usernames = card_usernames_map.setdefault(binding.card_id, [])
                usernames.append(binding.username)

            active_device_rows = self.db.query(
                CardDevice.card_id,
                func.count(CardDevice.id)
            ).filter(
                CardDevice.card_id.in_(card_ids),
                CardDevice.status == CardDeviceStatus.ACTIVE
            ).group_by(CardDevice.card_id).all()
            bind_device_count_map = {card_id: count for card_id, count in active_device_rows}

            app_name_map = {card.app_id: card.app.app_name if card.app else "未知应用" for card in cards}

            card_list = []
            for card in cards:
                related_usernames = card_usernames_map.get(card.id, [])
                
                card_list.append({
                    "id": card.id,
                    "app_id": card.app_id,
                    "app_name": app_name_map.get(card.app_id, "未知应用"),
                    "card_key": card.card_key,
                    "status": card.status.value,
                    "is_expired": bool(card.expire_time and card.expire_time < now),
                    "expire_time": card.expire_time,
                    "max_device_count": card.max_device_count,
                    "permissions": card.permissions,
                    "remark": card.remark,
                    "bind_user_count": len(related_usernames),
                    "related_usernames": related_usernames,
                    "bind_device_count": bind_device_count_map.get(card.id, 0),
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
            self._sync_card_usage_statuses([card.id])
            self.db.commit()
            
            logger.info(
                f"更新卡密状态成功: card_id={card_id}, "
                f"request_status={status}, final_status={card.status.value}"
            )
            return True, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新卡密状态失败: {e}")
            return False, f"更新卡密状态失败: {str(e)}"

    def update_card_expire_time(
        self,
        card_id: int,
        expire_time: datetime
    ) -> Tuple[bool, Optional[str]]:
        """
        更新卡密过期时间

        Args:
            card_id: 卡密ID
            expire_time: 新的过期时间

        Returns:
            (是否成功, 错误信息)
        """
        try:
            card = self.db.query(Card).filter(Card.id == card_id).first()
            if not card:
                return False, "卡密不存在"

            old_expire_time = card.expire_time
            card.expire_time = expire_time
            self._sync_card_usage_statuses([card.id])
            self.db.commit()

            logger.info(
                f"更新卡密过期时间成功: card_id={card_id}, "
                f"old_expire_time={old_expire_time}, new_expire_time={expire_time}"
            )
            return True, None

        except Exception as e:
            self.db.rollback()
            logger.error(f"更新卡密过期时间失败: card_id={card_id}, error={e}")
            return False, f"更新卡密过期时间失败: {str(e)}"
    
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
        card_key: Optional[str] = None,
        username: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Dict], int, Optional[str]]:
        """
        查询设备列表
        
        Args:
            page: 页码
            size: 每页数量
            card_id: 卡密ID筛选
            user_id: 用户ID筛选
            card_key: 卡密字符串筛选
            username: 用户名筛选
            status: 状态筛选
            
        Returns:
            (设备列表, 总数, 错误信息)
        """
        try:
            query = self.db.query(CardDevice)

            # 卡密筛选
            if card_id:
                query = query.filter(CardDevice.card_id == card_id)

            # 卡密字符串筛选
            if card_key:
                card_id_subquery = self.db.query(Card.id).filter(
                    Card.card_key.ilike(f"%{card_key.strip()}%")
                )
                query = query.filter(CardDevice.card_id.in_(card_id_subquery))

            # 用户筛选
            if user_id:
                # 使用子查询按卡密筛选，避免直接关联 user_cards 后造成设备记录重复。
                user_card_subquery = self.db.query(UserCard.card_id).filter(
                    UserCard.user_id == user_id,
                    UserCard.status == "active"
                )
                query = query.filter(CardDevice.card_id.in_(user_card_subquery))

            # 用户名筛选
            if username:
                username_card_subquery = self.db.query(UserCard.card_id).join(
                    User, User.id == UserCard.user_id
                ).filter(
                    UserCard.status == "active",
                    User.username.ilike(f"%{username.strip()}%")
                )
                query = query.filter(CardDevice.card_id.in_(username_card_subquery))

            # 状态筛选
            if status:
                query = query.filter(CardDevice.status == status)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            devices = query.order_by(CardDevice.bind_time.desc()).offset((page - 1) * size).limit(size).all()

            if not devices:
                return [], total, None

            card_ids = list({device.card_id for device in devices})

            # 批量查询卡密，避免循环内 N+1。
            cards = self.db.query(Card.id, Card.card_key).filter(Card.id.in_(card_ids)).all()
            card_key_map = {card.id: card.card_key for card in cards}

            # 批量聚合同一卡密下的有效绑定用户，设备页需要按“多用户”语义展示。
            user_bindings = self.db.query(
                UserCard.card_id,
                User.id,
                User.username
            ).join(User, User.id == UserCard.user_id).filter(
                UserCard.card_id.in_(card_ids),
                UserCard.status == "active"
            ).all()

            card_user_map: Dict[int, List[Dict[str, Union[int, str]]]] = {}
            for binding in user_bindings:
                related_users = card_user_map.setdefault(binding.card_id, [])
                related_users.append({
                    "id": binding.id,
                    "username": binding.username
                })

            # 构建返回数据
            device_list = []
            for device in devices:
                related_users = card_user_map.get(device.card_id, [])
                related_user_ids = [user["id"] for user in related_users]
                related_usernames = [user["username"] for user in related_users]

                device_list.append({
                    "id": device.id,
                    "card_id": device.card_id,
                    "card_key": card_key_map.get(device.card_id, "未知"),
                    "device_id": device.device_id,
                    "device_name": device.device_name,
                    "related_user_ids": related_user_ids,
                    "related_usernames": related_usernames,
                    "related_user_count": len(related_usernames),
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
            logger.info("[管理员服务] 开始汇总系统统计数据")
            if self._sync_card_usage_statuses():
                self.db.commit()
                logger.info("[管理员服务] 统计前已同步卡密使用状态，已提交数据库事务")

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

            # 趋势统计
            user_trend = self._build_recent_creation_trend(User)
            device_trend = self._build_recent_creation_trend(CardDevice)
            card_trend = self._build_recent_creation_trend(Card)
            app_trend = self._build_recent_creation_trend(App)
            
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
                },
                "trends": {
                    "labels": user_trend["labels"],
                    "daily_new": {
                        "users": user_trend["daily"],
                        "devices": device_trend["daily"],
                        "cards": card_trend["daily"],
                        "apps": app_trend["daily"]
                    },
                    "cumulative": {
                        "users": user_trend["cumulative"],
                        "devices": device_trend["cumulative"],
                        "cards": card_trend["cumulative"],
                        "apps": app_trend["cumulative"]
                    }
                }
            }

            logger.info(
                "[管理员服务] 系统统计汇总完成："
                f"users={statistics['users']}，"
                f"cards={statistics['cards']}，"
                f"devices={statistics['devices']}，"
                f"apps={statistics['apps']}，"
                f"trend_labels={statistics['trends']['labels']}"
            )
            
            return statistics, None
            
        except Exception as e:
            logger.error(f"获取统计数据失败: {e}")
            return {}, f"获取统计数据失败: {str(e)}"
