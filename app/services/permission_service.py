"""
权限校验服务层
处理权限验证的核心业务逻辑
"""
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User, UserStatus
from app.models.card import Card, CardStatus
from app.models.user_card import UserCard, UserCardStatus
from app.models.card_device import CardDevice, CardDeviceStatus
from app.core.logging_uru import logger


class PermissionService:
    """权限校验服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_permission(
        self,
        user_id: int,
        device_id: str,
        permission: str
    ) -> Tuple[bool, str, Optional[datetime]]:
        """
        检查用户在指定设备上是否有指定权限
        
        这是核心的权限校验逻辑，执行9步验证流程：
        1. 查询用户状态
        2. 验证用户是否被封禁
        3. 查询用户绑定的卡密
        4. 验证卡密状态
        5. 验证卡密是否过期
        6. 验证设备绑定
        7. 验证设备状态
        8. 验证权限配置
        9. 更新设备活跃时间
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            permission: 权限标识（如 "wechat", "ximalaya"）
            
        Returns:
            (是否允许, 提示信息, 卡密过期时间)
            
        Example:
            >>> allowed, message, expire_time = permission_service.check_permission(1, "device-001", "wechat")
            >>> if allowed:
            >>>     print("权限验证通过")
        """
        
        # 步骤 1: 查询用户状态
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"权限校验失败: 用户不存在 (user_id={user_id})")
            return False, "用户不存在", None
        
        # 步骤 2: 验证用户是否被封禁
        if user.status == UserStatus.BANNED:
            logger.warning(f"权限校验失败: 用户已被封禁 (user_id={user_id}, username={user.username})")
            return False, "用户已被封禁", None
        
        # 步骤 3: 查询用户绑定的卡密
        user_cards = self.db.query(UserCard, Card).join(
            Card, UserCard.card_id == Card.id
        ).filter(
            and_(
                UserCard.user_id == user_id,
                UserCard.status == UserCardStatus.ACTIVE
            )
        ).all()
        
        if not user_cards:
            logger.warning(f"权限校验失败: 用户未绑定卡密 (user_id={user_id}, username={user.username})")
            return False, "未绑定卡密", None
        
        # 遍历用户的所有卡密，寻找有效的卡密
        for user_card, card in user_cards:
            # 步骤 4: 验证卡密状态
            if card.status == CardStatus.DISABLED:
                logger.debug(f"跳过禁用的卡密: card_id={card.id}")
                continue
            
            # 步骤 5: 验证卡密是否过期
            if card.expire_time < datetime.now():
                logger.debug(f"跳过已过期的卡密: card_id={card.id}, expire_time={card.expire_time}")
                continue
            
            # 步骤 6: 验证设备绑定
            device_binding = self.db.query(CardDevice).filter(
                and_(
                    CardDevice.card_id == card.id,
                    CardDevice.device_id == device_id
                )
            ).first()
            
            if not device_binding:
                logger.debug(f"跳过未绑定此设备的卡密: card_id={card.id}, device_id={device_id}")
                continue
            
            # 步骤 7: 验证设备状态
            if device_binding.status == CardDeviceStatus.DISABLED:
                logger.warning(
                    f"权限校验失败: 设备已被禁用 "
                    f"(user_id={user_id}, card_id={card.id}, device_id={device_id})"
                )
                return False, "设备已被禁用", None
            
            # 步骤 8: 验证权限配置
            # permissions 可能是 list 或 dict 或 None 或 str(JSON字符串)
            card_permissions = card.permissions
            
            # 处理 None 的情况
            if card_permissions is None:
                logger.debug(f"卡密没有权限配置: card_id={card.id}")
                continue
            
            # 如果是字符串，尝试解析为 JSON
            if isinstance(card_permissions, str):
                import json
                try:
                    card_permissions = json.loads(card_permissions)
                    logger.debug(f"解析JSON字符串: card_id={card.id}, permissions={card_permissions}")
                except json.JSONDecodeError:
                    logger.error(f"无法解析卡密权限配置: {card_permissions}")
                    continue
            
            # 处理 list 的情况
            if isinstance(card_permissions, list):
                if permission not in card_permissions:
                    logger.debug(
                        f"权限不在卡密权限列表中: "
                        f"permission={permission}, card_permissions={card_permissions}"
                    )
                    continue
            
            # 处理 dict 的情况（例如 {"wechat": true, "ximalaya": false}）
            elif isinstance(card_permissions, dict):
                if permission not in card_permissions:
                    logger.debug(
                        f"权限不在卡密权限配置中: "
                        f"permission={permission}, card_permissions={card_permissions}"
                    )
                    continue
                
                # 检查权限值（如果是 bool 类型）
                if isinstance(card_permissions[permission], bool):
                    if not card_permissions[permission]:
                        logger.debug(
                            f"权限被设置为 false: "
                            f"permission={permission}, value={card_permissions[permission]}"
                        )
                        continue
            
            # 如果执行到这里，说明所有验证都通过了
            
            # 步骤 9: 更新设备最后活跃时间
            device_binding.last_active_at = datetime.now()
            self.db.commit()
            
            logger.info(
                f"权限校验通过: user_id={user_id}, username={user.username}, "
                f"device_id={device_id}, permission={permission}, "
                f"card_id={card.id}, expire_time={card.expire_time}"
            )
            
            return True, "权限验证通过", card.expire_time
        
        # 如果所有卡密都不满足条件
        logger.warning(
            f"权限校验失败: 没有有效的卡密满足条件 "
            f"(user_id={user_id}, device_id={device_id}, permission={permission})"
        )
        return False, "没有有效的卡密或权限配置不匹配", None
    
    def batch_check_permissions(
        self,
        user_id: int,
        device_id: str,
        permissions: list
    ) -> dict:
        """
        批量检查多个权限
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            permissions: 权限列表
            
        Returns:
            权限检查结果字典
            
        Example:
            >>> results = permission_service.batch_check_permissions(
            ...     user_id=1,
            ...     device_id="device-001",
            ...     permissions=["wechat", "ximalaya", "douyin"]
            ... )
            >>> # 返回: {"wechat": True, "ximalaya": True, "douyin": False}
        """
        results = {}
        
        for permission in permissions:
            allowed, message, expire_time = self.check_permission(
                user_id, device_id, permission
            )
            results[permission] = allowed
        
        logger.info(
            f"批量权限校验完成: user_id={user_id}, device_id={device_id}, "
            f"results={results}"
        )
        
        return results
    
    def get_user_permissions(
        self,
        user_id: int,
        device_id: str
    ) -> Tuple[bool, list, Optional[datetime]]:
        """
        获取用户在指定设备上的所有权限
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            
        Returns:
            (是否有效, 权限列表, 过期时间)
            
        Example:
            >>> valid, permissions, expire_time = permission_service.get_user_permissions(1, "device-001")
            >>> if valid:
            >>>     print(f"用户拥有的权限: {permissions}")
        """
        # 查询用户状态
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.status == UserStatus.BANNED:
            return False, [], None
        
        # 查询用户绑定的卡密
        user_cards = self.db.query(UserCard, Card).join(
            Card, UserCard.card_id == Card.id
        ).filter(
            and_(
                UserCard.user_id == user_id,
                UserCard.status == UserCardStatus.ACTIVE
            )
        ).all()
        logger.info(f"用户绑定的卡密: {user_cards}")
        all_permissions = set()
        expire_time = None
        
        for user_card, card in user_cards:
            logger.info(f"处理卡密: card_id={card.id}, status={card.status}, expire_time={card.expire_time}")
            
            # 验证卡密有效性
            if card.status == CardStatus.DISABLED:
                logger.info(f"卡密已禁用: card_id={card.id}")
                continue
            
            if card.expire_time < datetime.now():
                logger.info(f"卡密已过期: card_id={card.id}, expire_time={card.expire_time}")
                continue
            
            # 验证设备绑定
            device_binding = self.db.query(CardDevice).filter(
                and_(
                    CardDevice.card_id == card.id,
                    CardDevice.device_id == device_id,
                    CardDevice.status == CardDeviceStatus.ACTIVE
                )
            ).first()
            
            logger.info(f"设备绑定: device_binding={device_binding}")
            
            if not device_binding:
                logger.info(f"未找到设备绑定: card_id={card.id}, device_id={device_id}")
                continue
            
            # 收集权限
            if card.permissions:
                logger.debug(
                    f"卡密权限配置: card_id={card.id}, "
                    f"permissions={card.permissions}, "
                    f"type={type(card.permissions)}"
                )
                
                if isinstance(card.permissions, list):
                    all_permissions.update(card.permissions)
                elif isinstance(card.permissions, dict):
                    # 只添加值为 True 的权限
                    for perm, value in card.permissions.items():
                        if value is True or value == "true":
                            all_permissions.add(perm)
                elif isinstance(card.permissions, str):
                    # 如果是字符串，尝试解析为 JSON
                    import json
                    try:
                        parsed = json.loads(card.permissions)
                        if isinstance(parsed, list):
                            all_permissions.update(parsed)
                        elif isinstance(parsed, dict):
                            for perm, value in parsed.items():
                                if value is True or value == "true":
                                    all_permissions.add(perm)
                    except json.JSONDecodeError:
                        logger.error(f"无法解析卡密权限配置: {card.permissions}")
            else:
                logger.debug(f"卡密没有权限配置: card_id={card.id}")
            
            # 记录最晚的过期时间
            if expire_time is None or card.expire_time > expire_time:
                expire_time = card.expire_time
        
        permissions_list = sorted(list(all_permissions))
        
        logger.info(
            f"获取用户权限: user_id={user_id}, device_id={device_id}, "
            f"permissions={permissions_list}, expire_time={expire_time}"
        )
        
        return len(permissions_list) > 0, permissions_list, expire_time


def get_permission_service(db: Session) -> PermissionService:
    """
    获取权限服务实例
    
    Args:
        db: 数据库会话
        
    Returns:
        PermissionService实例
    """
    return PermissionService(db)
