"""
功能权限服务层
提供功能权限的增删改查以及卡密权限关联管理
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.app import App, AppStatus
from app.models.card import Card
from app.models.feature_permission import FeaturePermission, FeaturePermissionStatus
from app.services.card_pricing_service import calculate_card_price
from app.schemas.feature_permission import (
    FeaturePermissionAppInfo,
    FeaturePermissionExportAppGroup,
    FeaturePermissionExportFilter,
    FeaturePermissionExportPayload,
    FeaturePermissionSnapshotItem,
)


class FeaturePermissionService:
    """功能权限服务类"""

    def __init__(self, db: Session):
        self.db = db

    def create_permission(
        self,
        permission_key: str,
        permission_name: str,
        app_id: int,
        description: Optional[str] = None,
        price: Decimal = Decimal("0.00"),
        category: Optional[str] = None,
        icon: Optional[str] = None,
        sort_order: int = 0
    ) -> Tuple[Optional[FeaturePermission], Optional[str]]:
        """
        创建功能权限

        设计说明：
        - 新权限必须明确绑定应用，避免“看起来有分类、实际上只是字符串标签”的失真问题；
        - 不引入额外关联表，因为当前业务是“一条权限属于一个应用”，直接外键最简单稳定。
        """
        try:
            app = self._get_app_by_id(app_id)
            if not app:
                logger.warning(
                    f"创建功能权限失败: 所属应用不存在, permission_key={permission_key}, app_id={app_id}"
                )
                return None, "所属应用不存在，请先创建应用"

            existing = self.db.query(FeaturePermission).filter(
                FeaturePermission.permission_key == permission_key
            ).first()
            if existing:
                return None, f"权限标识 '{permission_key}' 已存在"

            permission = FeaturePermission(
                permission_key=permission_key,
                permission_name=permission_name,
                app_id=app.id,
                description=description,
                price=price,
                category=self._build_legacy_category(app=app, category=category),
                icon=icon,
                sort_order=sort_order,
                status=FeaturePermissionStatus.NORMAL.value
            )

            self.db.add(permission)
            self.db.commit()
            self.db.refresh(permission)

            logger.info(
                "创建功能权限成功: "
                f"permission_key={permission.permission_key}, permission_name={permission.permission_name}, "
                f"app_id={app.id}, app_key={app.app_key}, app_name={app.app_name}, price={permission.price}"
            )
            return permission, None

        except Exception as e:
            self.db.rollback()
            logger.exception(
                f"创建功能权限失败，事务已回滚: permission_key={permission_key}, error={e}"
            )
            return None, f"创建功能权限失败: {str(e)}"

    def update_permission(
        self,
        permission_id: int,
        permission_key: Optional[str] = None,
        permission_name: Optional[str] = None,
        app_id: Optional[int] = None,
        description: Optional[str] = None,
        price: Optional[Decimal] = None,
        category: Optional[str] = None,
        icon: Optional[str] = None,
        sort_order: Optional[int] = None,
        status: Optional[str] = None
    ) -> Tuple[Optional[FeaturePermission], Optional[str]]:
        """更新功能权限"""
        try:
            permission = self.db.query(FeaturePermission).filter(
                FeaturePermission.id == permission_id
            ).first()
            if not permission:
                return None, "功能权限不存在"

            if permission_key and permission_key != permission.permission_key:
                existing = self.db.query(FeaturePermission).filter(
                    FeaturePermission.permission_key == permission_key,
                    FeaturePermission.id != permission_id
                ).first()
                if existing:
                    return None, f"权限标识 '{permission_key}' 已被其他权限使用"
                permission.permission_key = permission_key

            target_app = permission.app
            if app_id is not None:
                target_app = self._get_app_by_id(app_id)
                if not target_app:
                    logger.warning(
                        f"更新功能权限失败: 所属应用不存在, permission_id={permission_id}, app_id={app_id}"
                    )
                    return None, "所属应用不存在，请先创建应用"
                permission.app_id = target_app.id

            if permission_name is not None:
                permission.permission_name = permission_name
            if description is not None:
                permission.description = description
            if price is not None:
                permission.price = price
            if category is not None or app_id is not None:
                permission.category = self._build_legacy_category(app=target_app, category=category)
            if icon is not None:
                permission.icon = icon
            if sort_order is not None:
                permission.sort_order = sort_order
            if status is not None:
                valid_statuses = [FeaturePermissionStatus.NORMAL.value, FeaturePermissionStatus.DISABLED.value]
                if status not in valid_statuses:
                    return None, "无效的状态值"
                permission.status = status

            self.db.commit()
            self.db.refresh(permission)

            logger.info(
                "更新功能权限成功: "
                f"permission_id={permission.id}, permission_key={permission.permission_key}, "
                f"app_id={permission.app_id}, app_name={permission.app.app_name if permission.app else '未绑定应用'}, "
                f"price={permission.price}"
            )
            return permission, None

        except Exception as e:
            self.db.rollback()
            logger.exception(f"更新功能权限失败，事务已回滚: permission_id={permission_id}, error={e}")
            return None, f"更新功能权限失败: {str(e)}"

    def delete_permission(self, permission_id: int) -> Tuple[bool, Optional[str]]:
        """删除功能权限"""
        try:
            permission = self.db.query(FeaturePermission).filter(
                FeaturePermission.id == permission_id
            ).first()
            if not permission:
                return False, "功能权限不存在"

            self.db.delete(permission)
            self.db.commit()

            logger.info(
                "删除功能权限成功: "
                f"permission_id={permission_id}, permission_key={permission.permission_key}"
            )
            return True, None

        except Exception as e:
            self.db.rollback()
            logger.exception(f"删除功能权限失败，事务已回滚: permission_id={permission_id}, error={e}")
            return False, f"删除功能权限失败: {str(e)}"

    def batch_delete_permissions(self, permission_ids: List[int]) -> Tuple[int, List[int], Optional[str]]:
        """
        批量删除功能权限。

        设计说明：
        - 权限元数据删除不影响卡密表的 JSON 结构完整性，但会让对应权限在后台不可再配置；
        - 因为这里是管理后台通用能力，所以统一提供批量删除，而不是只在页面上循环调单删接口。
        """
        if not permission_ids:
            return 0, [], "权限ID列表不能为空"

        deleted_count = 0
        failed_ids: List[int] = []

        for permission_id in permission_ids:
            try:
                permission = self.get_permission_by_id(permission_id)
                if not permission:
                    logger.warning(f"功能权限不存在，跳过删除: permission_id={permission_id}")
                    failed_ids.append(permission_id)
                    continue

                self.db.delete(permission)
                self.db.commit()
                deleted_count += 1
                logger.info(
                    "批量删除功能权限成功: "
                    f"permission_id={permission_id}, permission_key={permission.permission_key}"
                )
            except Exception as e:
                self.db.rollback()
                logger.exception(
                    f"批量删除功能权限失败，事务已回滚: permission_id={permission_id}, error={e}"
                )
                failed_ids.append(permission_id)

        return deleted_count, failed_ids, None

    def get_permission_by_id(self, permission_id: int) -> Optional[FeaturePermission]:
        """根据ID查询功能权限"""
        return self.db.query(FeaturePermission).filter(
            FeaturePermission.id == permission_id
        ).first()

    def get_permissions_list(
        self,
        page: int = 1,
        size: int = 20,
        app_id: Optional[int] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[FeaturePermission], int, Optional[str]]:
        """查询功能权限列表"""
        try:
            query = self.db.query(FeaturePermission)

            # app_id 是新的正式分类维度；category 仅保留给历史兼容查询。
            if app_id:
                query = query.filter(FeaturePermission.app_id == app_id)
            elif category:
                query = query.filter(FeaturePermission.category == category)

            if status:
                query = query.filter(FeaturePermission.status == status)

            if keyword:
                query = query.filter(or_(
                    FeaturePermission.permission_key.like(f"%{keyword}%"),
                    FeaturePermission.permission_name.like(f"%{keyword}%")
                ))

            total = query.count()
            permissions = query.order_by(
                FeaturePermission.sort_order.asc(),
                FeaturePermission.id.asc()
            ).offset((page - 1) * size).limit(size).all()

            logger.debug(
                "查询功能权限列表成功: "
                f"page={page}, size={size}, app_id={app_id}, status={status}, keyword={keyword}, total={total}"
            )
            return permissions, total, None

        except Exception as e:
            logger.exception(
                "查询功能权限列表失败: "
                f"page={page}, size={size}, app_id={app_id}, category={category}, status={status}, keyword={keyword}, error={e}"
            )
            return [], 0, f"查询功能权限列表失败: {str(e)}"

    def get_all_normal_permissions(
        self,
        app_id: Optional[int] = None,
        include_legacy_unassigned: bool = False
    ) -> List[FeaturePermission]:
        """获取所有正常状态的功能权限（不分页）"""
        query = self.db.query(FeaturePermission).filter(
            FeaturePermission.status == FeaturePermissionStatus.NORMAL.value
        )

        if app_id is not None:
            if include_legacy_unassigned:
                query = query.filter(
                    or_(
                        FeaturePermission.app_id == app_id,
                        FeaturePermission.app_id.is_(None)
                    )
                )
            else:
                query = query.filter(FeaturePermission.app_id == app_id)

        return query.order_by(
            FeaturePermission.sort_order.asc(),
            FeaturePermission.id.asc()
        ).all()

    def get_categories(self) -> List[str]:
        """
        获取所有权限分类

        当前“分类”已经统一收口为应用，所以这里直接返回所有应用名称。
        """
        apps = self.db.query(App).order_by(App.created_at.desc(), App.id.desc()).all()
        return [app.app_name for app in apps]

    def build_permissions_export_payload(
        self,
        permission_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """构建功能权限导出快照"""
        if not permission_keys:
            logger.warning("构建功能权限导出快照失败: 未提供任何权限标识")
            return None, "请选择要导出的权限"

        unique_permission_keys = list(dict.fromkeys(permission_keys))
        permissions = self.db.query(FeaturePermission).filter(
            FeaturePermission.permission_key.in_(unique_permission_keys)
        ).order_by(
            FeaturePermission.sort_order.asc(),
            FeaturePermission.id.asc()
        ).all()

        found_keys = {permission.permission_key for permission in permissions}
        missing_keys = [
            permission_key
            for permission_key in unique_permission_keys
            if permission_key not in found_keys
        ]
        if missing_keys:
            missing_text = "、".join(missing_keys)
            logger.warning(f"构建功能权限导出快照失败，存在无效权限标识: {missing_text}")
            return None, f"以下权限不存在，无法导出: {missing_text}"

        snapshot_items = [self._build_snapshot_item(permission) for permission in permissions]
        app_groups = self._build_export_app_groups(snapshot_items)

        payload = FeaturePermissionExportPayload(
            schema_version="feature_permissions.v2",
            exported_at=datetime.now(),
            total=len(snapshot_items),
            filters=FeaturePermissionExportFilter(
                page=1,
                size=len(snapshot_items),
                keyword="selected_permissions"
            ),
            permissions=snapshot_items,
            app_groups=app_groups
        )

        logger.info(
            "构建功能权限导出快照成功: "
            f"selected_count={len(unique_permission_keys)}, export_count={len(snapshot_items)}, "
            f"app_group_count={len(app_groups)}, permission_keys={unique_permission_keys}"
        )
        return payload.model_dump(mode="json", exclude_none=True), None

    def import_permissions_from_payload(
        self,
        payload: FeaturePermissionExportPayload
    ) -> Tuple[Optional[Dict[str, int]], Optional[str]]:
        """从导出快照导入功能权限"""
        try:
            permission_items = self._extract_permission_items_from_payload(payload)
            duplicate_keys = self._find_duplicate_permission_keys(permission_items)
            if duplicate_keys:
                duplicate_text = "、".join(sorted(duplicate_keys))
                logger.warning(f"导入功能权限失败，文件内存在重复权限标识: {duplicate_text}")
                return None, f"导入文件中存在重复的权限标识: {duplicate_text}"

            created_count = 0
            updated_count = 0
            created_app_count = 0

            logger.info(
                "开始导入功能权限快照: "
                f"schema_version={payload.schema_version}, total_count={len(permission_items)}, "
                f"app_group_count={len(payload.app_groups)}"
            )

            for item in permission_items:
                resolved_app, app_created = self._resolve_import_app(item)
                if app_created:
                    created_app_count += 1

                existing_permission = self.db.query(FeaturePermission).filter(
                    FeaturePermission.permission_key == item.permission_key
                ).first()

                if existing_permission:
                    logger.info(
                        "导入命中已有权限，准备更新: "
                        f"permission_key={item.permission_key}, "
                        f"target_app={resolved_app.app_key if resolved_app else '未绑定应用'}"
                    )
                    existing_permission.permission_name = item.permission_name
                    existing_permission.app_id = resolved_app.id if resolved_app else None
                    existing_permission.description = item.description
                    existing_permission.price = item.price
                    existing_permission.category = self._build_legacy_category(
                        app=resolved_app,
                        category=item.category
                    )
                    existing_permission.icon = item.icon
                    existing_permission.sort_order = item.sort_order
                    existing_permission.status = item.status
                    updated_count += 1
                    continue

                logger.info(
                    "导入命中新权限，准备创建: "
                    f"permission_key={item.permission_key}, "
                    f"target_app={resolved_app.app_key if resolved_app else '未绑定应用'}"
                )
                self.db.add(
                    FeaturePermission(
                        permission_key=item.permission_key,
                        permission_name=item.permission_name,
                        app_id=resolved_app.id if resolved_app else None,
                        description=item.description,
                        price=item.price,
                        category=self._build_legacy_category(app=resolved_app, category=item.category),
                        icon=item.icon,
                        sort_order=item.sort_order,
                        status=item.status
                    )
                )
                created_count += 1

            self.db.commit()

            summary = {
                "total_count": len(permission_items),
                "created_count": created_count,
                "updated_count": updated_count,
                "created_app_count": created_app_count,
            }
            logger.info(f"导入功能权限快照成功: {summary}")
            return summary, None

        except Exception as e:
            self.db.rollback()
            logger.exception(f"导入功能权限快照失败，事务已回滚: {e}")
            return None, f"导入功能权限失败: {str(e)}"

    def update_card_permissions(
        self,
        card_id: int,
        permission_keys: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """更新卡密的功能权限"""
        try:
            card = self.db.query(Card).filter(Card.id == card_id).first()
            if not card:
                return False, "卡密不存在"

            all_permissions = self.db.query(FeaturePermission).filter(
                FeaturePermission.permission_key.in_(permission_keys),
                or_(
                    FeaturePermission.app_id == card.app_id,
                    FeaturePermission.app_id.is_(None)
                )
            ).all()

            found_keys = {permission.permission_key for permission in all_permissions}
            invalid_keys = set(permission_keys) - found_keys
            if invalid_keys:
                invalid_keys_text = ", ".join(sorted(invalid_keys))
                logger.warning(
                    "更新卡密功能权限失败: 存在不属于当前应用的权限 "
                    f"card_id={card_id}, card_app_id={card.app_id}, invalid_keys={invalid_keys_text}"
                )
                return False, f"以下权限标识不存在或不属于当前卡密应用: {invalid_keys_text}"

            old_price = card.price
            card.permissions = permission_keys
            card.price = calculate_card_price(
                self.db,
                app_id=card.app_id,
                permissions=card.permissions,
                expire_time=card.expire_time,
                max_device_count=card.max_device_count
            )
            self.db.commit()

            logger.info(
                "更新卡密功能权限成功: "
                f"card_id={card_id}, card_app_id={card.app_id}, permissions={permission_keys}, "
                f"old_price={old_price}, new_price={card.price}"
            )
            return True, None

        except Exception as e:
            self.db.rollback()
            logger.exception(f"更新卡密功能权限失败，事务已回滚: card_id={card_id}, error={e}")
            return False, f"更新卡密功能权限失败: {str(e)}"

    @staticmethod
    def _find_duplicate_permission_keys(
        permission_items: List[FeaturePermissionSnapshotItem]
    ) -> List[str]:
        """
        检查导入文件中是否有重复 permission_key

        为什么单独抽成公共方法：
        - 重复标识不是接口层问题，而是导入业务的通用数据约束；
        - 后续如果 CLI、脚本、后台批量任务复用同一导入逻辑，也能共享这层校验。
        """
        seen_keys = set()
        duplicate_keys = set()

        for item in permission_items:
            if item.permission_key in seen_keys:
                duplicate_keys.add(item.permission_key)
                continue
            seen_keys.add(item.permission_key)

        return list(duplicate_keys)

    def get_card_permissions(
        self,
        card_id: int
    ) -> Tuple[List[str], Optional[str]]:
        """获取卡密的功能权限标识列表"""
        try:
            card = self.db.query(Card).filter(Card.id == card_id).first()
            if not card:
                return [], "卡密不存在"

            permissions = card.permissions if isinstance(card.permissions, list) else []
            logger.debug(
                f"获取卡密功能权限成功: card_id={card_id}, card_app_id={card.app_id}, permissions={permissions}"
            )
            return permissions, None

        except Exception as e:
            logger.exception(f"获取卡密功能权限失败: card_id={card_id}, error={e}")
            return [], f"获取卡密功能权限失败: {str(e)}"

    def _get_app_by_id(self, app_id: int) -> Optional[App]:
        """根据应用ID查询应用。"""
        return self.db.query(App).filter(App.id == app_id).first()

    def _build_legacy_category(
        self,
        app: Optional[App],
        category: Optional[str]
    ) -> Optional[str]:
        """
        兼容历史 category 字段。

        新设计里 category 不再是主分类，页面展示和导入导出都以应用为准。
        这里仍把应用名称镜像到 category，保证旧页面、旧脚本、旧导出文件仍能读到“分类”信息。
        """
        if app:
            return app.app_name
        return category

    def _build_app_info(self, permission: FeaturePermission) -> Optional[FeaturePermissionAppInfo]:
        """构造权限所属应用信息。"""
        if not permission.app:
            return None

        return FeaturePermissionAppInfo(
            app_id=permission.app.id,
            app_key=permission.app.app_key,
            app_name=permission.app.app_name
        )

    def _build_snapshot_item(self, permission: FeaturePermission) -> FeaturePermissionSnapshotItem:
        """构造导出快照项。"""
        return FeaturePermissionSnapshotItem(
            permission_key=permission.permission_key,
            permission_name=permission.permission_name,
            app=self._build_app_info(permission),
            description=permission.description,
            price=permission.price,
            category=self._build_legacy_category(permission.app, permission.category),
            icon=permission.icon,
            sort_order=permission.sort_order,
            status=permission.status
        )

    def _build_export_app_groups(
        self,
        snapshot_items: List[FeaturePermissionSnapshotItem]
    ) -> List[FeaturePermissionExportAppGroup]:
        """按所属应用构造导出分组，方便人工查看导出文件。"""
        group_map: Dict[str, Dict[str, Any]] = {}

        for item in snapshot_items:
            if item.app and (item.app.app_key or item.app.app_name):
                group_key = item.app.app_key or f"app_name:{item.app.app_name}"
                app_info = item.app
            else:
                group_key = "__legacy_unassigned__"
                app_info = FeaturePermissionAppInfo(
                    app_id=None,
                    app_key="legacy_unassigned",
                    app_name="未绑定应用"
                )

            group = group_map.setdefault(
                group_key,
                {
                    "app": app_info,
                    "permissions": []
                }
            )
            group["permissions"].append(item)

        app_groups: List[FeaturePermissionExportAppGroup] = []
        for group in group_map.values():
            app_groups.append(
                FeaturePermissionExportAppGroup(
                    app=group["app"],
                    total=len(group["permissions"]),
                    permissions=group["permissions"]
                )
            )

        app_groups.sort(key=lambda item: ((item.app.app_name or "未绑定应用"), (item.app.app_key or "")))
        return app_groups

    def _extract_permission_items_from_payload(
        self,
        payload: FeaturePermissionExportPayload
    ) -> List[FeaturePermissionSnapshotItem]:
        """
        从导出文件中提取待导入权限。

        兼容策略：
        - 新版导出文件优先读取 permissions；
        - 如果后续只保留 app_groups，也能从分组中还原；
        - 历史 v1 文件没有 app 信息时，仍允许导入，只是会保留为“未绑定应用”的旧权限。
        """
        if payload.permissions:
            return payload.permissions

        permission_items: List[FeaturePermissionSnapshotItem] = []
        for group in payload.app_groups:
            for permission in group.permissions:
                if permission.app is None:
                    permission_items.append(
                        FeaturePermissionSnapshotItem(
                            permission_key=permission.permission_key,
                            permission_name=permission.permission_name,
                            app=group.app,
                            description=permission.description,
                            price=permission.price,
                            category=permission.category,
                            icon=permission.icon,
                            sort_order=permission.sort_order,
                            status=permission.status
                        )
                    )
                    continue
                permission_items.append(permission)
        return permission_items

    def _resolve_import_app(
        self,
        item: FeaturePermissionSnapshotItem
    ) -> Tuple[Optional[App], bool]:
        """
        解析导入项所属应用，不存在时自动创建。

        返回：
        - App 对象或 None（历史未绑定应用数据）
        - 是否在本次导入过程中自动创建了应用
        """
        if not item.app:
            logger.warning(
                "导入权限缺少应用信息，将按历史未绑定应用处理: "
                f"permission_key={item.permission_key}"
            )
            return None, False

        app_key = (item.app.app_key or "").strip()
        app_name = (item.app.app_name or "").strip()

        if not app_key and not app_name:
            logger.warning(
                "导入权限应用信息为空，将按历史未绑定应用处理: "
                f"permission_key={item.permission_key}"
            )
            return None, False

        existing_app = None
        if app_key:
            existing_app = self.db.query(App).filter(App.app_key == app_key).first()
        if not existing_app and app_name:
            existing_app = self.db.query(App).filter(App.app_name == app_name).first()

        if existing_app:
            logger.info(
                "导入权限命中已有应用: "
                f"permission_key={item.permission_key}, app_id={existing_app.id}, "
                f"app_key={existing_app.app_key}, app_name={existing_app.app_name}"
            )
            return existing_app, False

        generated_app_key = app_key or self._generate_import_app_key(app_name or item.permission_key)
        generated_app_name = app_name or f"{item.permission_name}所属应用"

        new_app = App(
            app_key=generated_app_key,
            app_name=generated_app_name,
            status=AppStatus.NORMAL
        )
        self.db.add(new_app)
        # 这里用 flush 提前拿到应用ID，保证同一事务里创建权限时可以直接引用。
        self.db.flush()

        logger.info(
            "导入权限自动创建应用成功: "
            f"permission_key={item.permission_key}, app_id={new_app.id}, "
            f"app_key={new_app.app_key}, app_name={new_app.app_name}"
        )
        return new_app, True

    @staticmethod
    def _generate_import_app_key(seed_text: str) -> str:
        """为导入时缺少 app_key 的应用生成一个可读的 key。"""
        normalized = "".join(
            character.lower() if character.isalnum() else "_"
            for character in seed_text.strip()
        ).strip("_")

        if not normalized:
            normalized = "imported_app"

        return f"{normalized[:32]}_auto"
