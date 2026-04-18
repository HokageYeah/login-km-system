"""
权限校验服务层
处理权限验证的核心业务逻辑
"""
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
import json

from app.models.user import User, UserStatus, UserRole
from app.models.card import Card, CardStatus
from app.models.user_card import UserCard, UserCardStatus
from app.models.card_device import CardDevice, CardDeviceStatus
from app.models.feature_permission import FeaturePermission, FeaturePermissionStatus
from app.core.logging_uru import logger


CURRENT_CARD_PERMISSION_DENIED_MESSAGE = "当前卡密没有该系统权限，请切换卡密或联系管理员开通权限"
DEVICE_LIMIT_EXCEEDED_MESSAGE_TEMPLATE = "当前卡密绑定设备数量已达上限（{max_device_count}台），请先解绑其他设备后再使用当前登录设备"


class PermissionService:
    """权限校验服务类"""
    
    def __init__(self, db: Session):
        self.db = db

    def _is_admin_user(self, user: User) -> bool:
        """
        判断用户是否为管理员

        管理员属于系统级操作身份，不应再被卡密绑定和设备绑定限制。
        将判断统一收口到服务层，避免各个接口各自打补丁。
        """
        return user.role == UserRole.ADMIN

    def _get_normal_permission_keys(self) -> list:
        """
        获取系统内已启用的权限标识列表。

        权限查询、管理员默认权限、无候选权限时的兜底探测，都应基于同一份权限元数据，
        避免不同入口各自拼接权限集合导致裁决口径不一致。
        """
        permissions = self.db.query(FeaturePermission).filter(
            FeaturePermission.status == FeaturePermissionStatus.NORMAL.value
        ).order_by(
            FeaturePermission.sort_order.asc(),
            FeaturePermission.id.asc()
        ).all()

        return [item.permission_key for item in permissions]

    def _get_admin_permissions(self) -> list:
        """
        获取管理员可见的全部权限标识

        管理员天然拥有全部权限，因此这里优先返回权限元数据表中的正常权限，
        让“查询我的权限”与实际的权限校验结果保持一致。
        """
        return self._get_normal_permission_keys()

    def _get_user_cards(self, user_id: int, card_id: Optional[int] = None):
        """
        查询用户绑定的有效关系，可选按当前卡密收窄。

        当前卡密是权限裁决的业务边界：客户端切换到某张卡密后，
        服务端只能使用这张卡密的权限，不能把同设备上的其他卡密权限合并进来。
        """
        filters = [
            UserCard.user_id == user_id,
            UserCard.status == UserCardStatus.ACTIVE
        ]

        if card_id is not None:
            filters.append(UserCard.card_id == card_id)

        return self.db.query(UserCard, Card).join(
            Card, UserCard.card_id == Card.id
        ).filter(and_(*filters)).all()

    def _parse_permissions(self, card: Card) -> Optional[object]:
        """
        解析卡密权限配置，保持 list / dict / JSON 字符串的历史兼容。
        """
        card_permissions = card.permissions

        if card_permissions is None:
            return None

        if isinstance(card_permissions, str):
            try:
                parsed_permissions = json.loads(card_permissions)
                logger.debug(
                    f"解析JSON字符串权限配置: card_id={card.id}, "
                    f"permissions={parsed_permissions}"
                )
                return parsed_permissions
            except json.JSONDecodeError:
                logger.error(f"无法解析卡密权限配置: card_id={card.id}, permissions={card_permissions}")
                return None

        return card_permissions

    def _card_has_permission(self, card: Card, permission: str) -> bool:
        """
        判断单张卡密是否包含指定权限。

        该方法集中处理权限格式差异，避免单项校验、批量校验、权限列表查询各自维护一套规则。
        """
        card_permissions = self._parse_permissions(card)

        if card_permissions is None:
            logger.debug(f"卡密没有权限配置: card_id={card.id}")
            return False

        if isinstance(card_permissions, list):
            return permission in card_permissions

        if isinstance(card_permissions, dict):
            if permission not in card_permissions:
                return False

            value = card_permissions[permission]
            if isinstance(value, bool):
                return value

            if isinstance(value, str):
                return value.lower() == "true"

            return bool(value)

        logger.warning(
            f"卡密权限配置类型不支持: card_id={card.id}, "
            f"type={type(card_permissions)}"
        )
        return False

    def _extract_permission_keys(self, card: Card) -> list:
        """
        从单张卡密中提取可用权限列表，规则与单项权限校验保持一致。
        """
        card_permissions = self._parse_permissions(card)

        if card_permissions is None:
            logger.debug(f"卡密没有权限配置: card_id={card.id}")
            return []

        if isinstance(card_permissions, list):
            return card_permissions

        if isinstance(card_permissions, dict):
            return [
                permission
                for permission, value in card_permissions.items()
                if value is True or (isinstance(value, str) and value.lower() == "true")
            ]

        logger.warning(
            f"卡密权限配置类型不支持: card_id={card.id}, "
            f"type={type(card_permissions)}"
        )
        return []

    def _count_active_devices(self, card_id: int) -> int:
        """
        统计卡密当前活跃设备数。

        设备上限判断、管理员修改设备上限、卡密绑定校验都应该遵循同一个“active 设备数”口径，
        避免各条链路对 disabled 设备是否计入产生分歧。
        """
        return self.db.query(CardDevice).filter(
            CardDevice.card_id == card_id,
            CardDevice.status == CardDeviceStatus.ACTIVE
        ).count()

    def _get_configured_permission_keys(
        self,
        user_id: int,
        card_id: Optional[int] = None
    ) -> list:
        """
        获取当前裁决范围内配置过的权限候选集。

        “查询我的权限”不应自己重复实现卡密、设备、过期等判断，
        这里只负责提取候选 permission_key，实际准入仍统一交给 check_permission。
        """
        permission_keys = set()

        for _, card in self._get_user_cards(user_id=user_id, card_id=card_id):
            permission_keys.update(self._extract_permission_keys(card))

        return sorted(permission_keys)
    
    def check_permission(
        self,
        user_id: int,
        device_id: str,
        permission: str,
        card_id: Optional[int] = None,
        touch_last_active: bool = True
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
            card_id: 当前使用的卡密ID；不传时按用户和设备兜底查询
            touch_last_active: 是否更新设备最后活跃时间
            
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

        # 管理员是系统级身份，不需要绑定卡密和设备即可访问所有权限接口
        if self._is_admin_user(user):
            logger.info(
                f"权限校验通过: 管理员免卡密校验 "
                f"(user_id={user_id}, username={user.username}, permission={permission})"
            )
            return True, "管理员默认拥有全部权限", None

        # 步骤 3: 查询用户绑定的卡密。传入 card_id 时只校验当前卡密，避免同设备多卡权限串用。
        user_cards = self._get_user_cards(user_id=user_id, card_id=card_id)
        
        if not user_cards:
            if card_id is not None:
                logger.warning(
                    f"权限校验失败: 当前用户未绑定指定卡密 "
                    f"(user_id={user_id}, username={user.username}, card_id={card_id})"
                )
                return False, "当前用户未绑定指定卡密", None

            logger.warning(f"权限校验失败: 用户未绑定卡密 (user_id={user_id}, username={user.username})")
            return False, "未绑定卡密", None
        
        has_available_card_after_expire_check = False
        has_expired_card = False
        device_limit_exceeded_message: Optional[str] = None

        # 遍历用户的所有卡密，寻找有效的卡密
        for user_card, card in user_cards:
            # 步骤 4: 验证卡密状态
            if card.status == CardStatus.DISABLED:
                logger.debug(f"跳过禁用的卡密: card_id={card.id}")
                continue

            # 步骤 5: 验证卡密是否过期
            if card.expire_time < datetime.now():
                has_expired_card = True
                logger.debug(f"跳过已过期的卡密: card_id={card.id}, expire_time={card.expire_time}")
                continue

            has_available_card_after_expire_check = True

            # 步骤 6: 先验证权限配置。
            # 只有在卡密本身具备目标权限时，才有必要继续判断“当前设备为什么不能用这张卡”，
            # 否则会把本质上的“权限不匹配”误报成“设备超限”。
            if not self._card_has_permission(card, permission):
                logger.debug(
                    f"权限不在当前卡密权限配置中: "
                    f"card_id={card.id}, permission={permission}"
                )
                if card_id is not None:
                    logger.warning(
                        f"权限校验失败: 当前卡密缺少系统权限 "
                        f"(user_id={user_id}, card_id={card.id}, "
                        f"device_id={device_id}, permission={permission})"
                    )
                    return False, CURRENT_CARD_PERMISSION_DENIED_MESSAGE, None
                continue

            # 步骤 7: 验证设备绑定
            device_binding = self.db.query(CardDevice).filter(
                and_(
                    CardDevice.card_id == card.id,
                    CardDevice.device_id == device_id
                )
            ).first()

            if not device_binding:
                active_device_count = self._count_active_devices(card.id)

                # 当前登录设备不在绑定列表里，同时卡密活跃设备数已经达到或超过上限时，
                # 直接给出精准错误，帮助客户端和管理员快速定位为“设备数超限”问题。
                if active_device_count >= card.max_device_count:
                    device_limit_exceeded_message = DEVICE_LIMIT_EXCEEDED_MESSAGE_TEMPLATE.format(
                        max_device_count=card.max_device_count
                    )
                    logger.warning(
                        f"权限校验失败: 当前登录设备未绑定且卡密设备数已达上限 "
                        f"(user_id={user_id}, card_id={card.id}, device_id={device_id}, "
                        f"active_device_count={active_device_count}, max_device_count={card.max_device_count}, "
                        f"permission={permission})"
                    )
                    if card_id is not None:
                        return False, device_limit_exceeded_message, None
                else:
                    logger.debug(
                        f"跳过未绑定此设备的卡密: card_id={card.id}, device_id={device_id}, "
                        f"active_device_count={active_device_count}, max_device_count={card.max_device_count}"
                    )
                continue

            # 步骤 8: 验证设备状态
            if device_binding.status == CardDeviceStatus.DISABLED:
                logger.warning(
                    f"权限校验失败: 设备已被禁用 "
                    f"(user_id={user_id}, card_id={card.id}, device_id={device_id})"
                )
                return False, "设备已被禁用", None
            
            # 如果执行到这里，说明所有验证都通过了
            
            # 步骤 9: 更新设备最后活跃时间
            if touch_last_active:
                device_binding.last_active_at = datetime.now()
                self.db.commit()
            
            logger.info(
                f"权限校验通过: user_id={user_id}, username={user.username}, "
                f"device_id={device_id}, permission={permission}, "
                f"card_id={card.id}, expire_time={card.expire_time}"
            )
            
            return True, "权限验证通过", card.expire_time
        
        if has_expired_card and not has_available_card_after_expire_check:
            logger.warning(
                f"权限校验失败: 用户绑定的卡密已过期 "
                f"(user_id={user_id}, device_id={device_id}, permission={permission})"
            )
            return False, "卡密已过期，请绑定新卡密", None

        if device_limit_exceeded_message:
            logger.warning(
                f"权限校验失败: 当前登录设备触发卡密设备上限 "
                f"(user_id={user_id}, device_id={device_id}, permission={permission}, "
                f"message={device_limit_exceeded_message})"
            )
            return False, device_limit_exceeded_message, None

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
        permissions: list,
        card_id: Optional[int] = None
    ) -> dict:
        """
        批量检查多个权限
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            permissions: 权限列表
            card_id: 当前使用的卡密ID；不传时按用户和设备兜底查询
            
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
                user_id, device_id, permission, card_id=card_id
            )
            results[permission] = allowed
        
        logger.info(
            f"批量权限校验完成: user_id={user_id}, device_id={device_id}, "
            f"results={results}"
        )
        
        return results
    
    def get_user_permissions_with_message(
        self,
        user_id: int,
        device_id: str,
        card_id: Optional[int] = None
    ) -> Tuple[bool, list, Optional[datetime], str]:
        """
        获取用户在指定设备上的所有权限，并返回统一校验链上的提示信息。

        Args:
            user_id: 用户ID
            device_id: 设备ID
            card_id: 当前使用的卡密ID；不传时按用户和设备兜底查询
            
        Returns:
            (是否有效, 权限列表, 过期时间, 提示信息)
            
        Example:
            >>> valid, permissions, expire_time = permission_service.get_user_permissions(1, "device-001")
            >>> if valid:
            >>>     print(f"用户拥有的权限: {permissions}")
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"获取用户权限失败: 用户不存在 (user_id={user_id})")
            return False, [], None, "用户不存在"

        if user.status == UserStatus.BANNED:
            logger.warning(
                f"获取用户权限失败: 用户已被封禁 "
                f"(user_id={user_id}, username={user.username})"
            )
            return False, [], None, "用户已被封禁"

        if self._is_admin_user(user):
            admin_permissions = self._get_admin_permissions()
            logger.info(
                f"获取管理员权限: user_id={user_id}, username={user.username}, "
                f"permissions={admin_permissions}"
            )
            return True, admin_permissions, None, "管理员默认拥有全部权限"

        permission_candidates = self._get_configured_permission_keys(
            user_id=user_id,
            card_id=card_id
        )
        all_permissions = []
        expire_time = None
        failure_message = "没有有效的卡密或权限配置不匹配"

        if not permission_candidates:
            permission_candidates = self._get_normal_permission_keys()[:1] or ["__permission_probe__"]

        for permission in permission_candidates:
            allowed, message, current_expire_time = self.check_permission(
                user_id=user_id,
                device_id=device_id,
                permission=permission,
                card_id=card_id,
                touch_last_active=False
            )

            if allowed:
                all_permissions.append(permission)
                if expire_time is None or (
                    current_expire_time is not None and current_expire_time > expire_time
                ):
                    expire_time = current_expire_time
                continue

            if failure_message == "没有有效的卡密或权限配置不匹配":
                failure_message = message

        permissions_list = sorted(all_permissions)
        
        logger.info(
            f"获取用户权限: user_id={user_id}, device_id={device_id}, "
            f"card_id={card_id}, permissions={permissions_list}, "
            f"expire_time={expire_time}, message={failure_message}"
        )

        if permissions_list:
            return True, permissions_list, expire_time, "权限验证通过"

        return False, [], None, failure_message

    def get_user_permissions(
        self,
        user_id: int,
        device_id: str,
        card_id: Optional[int] = None
    ) -> Tuple[bool, list, Optional[datetime]]:
        """
        获取用户在指定设备上的所有权限。

        对外继续保持原有返回结构，避免影响现有调用方；
        需要统一错误信息时，应使用 get_user_permissions_with_message。
        """
        has_permission, permissions, expire_time, _ = self.get_user_permissions_with_message(
            user_id=user_id,
            device_id=device_id,
            card_id=card_id
        )
        return has_permission, permissions, expire_time


def get_permission_service(db: Session) -> PermissionService:
    """
    获取权限服务实例
    
    Args:
        db: 数据库会话
        
    Returns:
        PermissionService实例
    """
    return PermissionService(db)
