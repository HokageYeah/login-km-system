"""
功能权限服务层
提供功能权限的增删改查以及卡密权限关联管理
"""
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from loguru import logger

from app.models.feature_permission import FeaturePermission, FeaturePermissionStatus
from app.models.card import Card
from app.schemas.feature_permission import (
    FeaturePermissionExportPayload,
    FeaturePermissionExportFilter,
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
        description: Optional[str] = None,
        category: Optional[str] = None,
        icon: Optional[str] = None,
        sort_order: int = 0
    ) -> Tuple[Optional[FeaturePermission], Optional[str]]:
        """
        创建功能权限
        
        Args:
            permission_key: 权限标识
            permission_name: 权限名称
            description: 权限描述
            category: 权限分类
            icon: 图标
            sort_order: 排序
            
        Returns:
            (功能权限对象, 错误信息)
        """
        try:
            # 检查权限标识是否已存在
            existing = self.db.query(FeaturePermission).filter(
                FeaturePermission.permission_key == permission_key
            ).first()
            
            if existing:
                return None, f"权限标识 '{permission_key}' 已存在"
            
            # 创建功能权限
            permission = FeaturePermission(
                permission_key=permission_key,
                permission_name=permission_name,
                description=description,
                category=category,
                icon=icon,
                sort_order=sort_order,
                status=FeaturePermissionStatus.NORMAL.value
            )
            
            self.db.add(permission)
            self.db.commit()
            self.db.refresh(permission)
            
            logger.info(f"创建功能权限成功: {permission_key} - {permission_name}")
            return permission, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建功能权限失败: {e}")
            return None, f"创建功能权限失败: {str(e)}"
    
    def update_permission(
        self,
        permission_id: int,
        permission_key: Optional[str] = None,
        permission_name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        icon: Optional[str] = None,
        sort_order: Optional[int] = None,
        status: Optional[str] = None
    ) -> Tuple[Optional[FeaturePermission], Optional[str]]:
        """
        更新功能权限
        
        Args:
            permission_id: 功能权限ID
            permission_key: 权限标识
            permission_name: 权限名称
            description: 权限描述
            category: 权限分类
            icon: 图标
            sort_order: 排序
            status: 状态
            
        Returns:
            (功能权限对象, 错误信息)
        """
        try:
            permission = self.db.query(FeaturePermission).filter(
                FeaturePermission.id == permission_id
            ).first()
            
            if not permission:
                return None, "功能权限不存在"
            
            # 如果要修改权限标识，检查是否与其他权限冲突
            if permission_key and permission_key != permission.permission_key:
                existing = self.db.query(FeaturePermission).filter(
                    FeaturePermission.permission_key == permission_key,
                    FeaturePermission.id != permission_id
                ).first()
                
                if existing:
                    return None, f"权限标识 '{permission_key}' 已被其他权限使用"
                
                permission.permission_key = permission_key
            
            # 更新其他字段
            if permission_name is not None:
                permission.permission_name = permission_name
            if description is not None:
                permission.description = description
            if category is not None:
                permission.category = category
            if icon is not None:
                permission.icon = icon
            if sort_order is not None:
                permission.sort_order = sort_order
            if status is not None:
                # 验证状态值
                valid_statuses = [FeaturePermissionStatus.NORMAL.value, FeaturePermissionStatus.DISABLED.value]
                if status not in valid_statuses:
                    return None, "无效的状态值"
                permission.status = status
            
            self.db.commit()
            self.db.refresh(permission)
            
            logger.info(f"更新功能权限成功: ID {permission_id}")
            return permission, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新功能权限失败: {e}")
            return None, f"更新功能权限失败: {str(e)}"
    
    def delete_permission(self, permission_id: int) -> Tuple[bool, Optional[str]]:
        """
        删除功能权限
        
        Args:
            permission_id: 功能权限ID
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            permission = self.db.query(FeaturePermission).filter(
                FeaturePermission.id == permission_id
            ).first()
            
            if not permission:
                return False, "功能权限不存在"
            
            self.db.delete(permission)
            self.db.commit()
            
            logger.info(f"删除功能权限成功: {permission.permission_key}")
            return True, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除功能权限失败: {e}")
            return False, f"删除功能权限失败: {str(e)}"
    
    def get_permission_by_id(
        self,
        permission_id: int
    ) -> Optional[FeaturePermission]:
        """
        根据ID查询功能权限
        
        Args:
            permission_id: 功能权限ID
            
        Returns:
            功能权限对象
        """
        return self.db.query(FeaturePermission).filter(
            FeaturePermission.id == permission_id
        ).first()
    
    def get_permissions_list(
        self,
        page: int = 1,
        size: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[FeaturePermission], int, Optional[str]]:
        """
        查询功能权限列表
        
        Args:
            page: 页码
            size: 每页数量
            category: 分类筛选
            status: 状态筛选
            keyword: 关键词搜索（权限标识、权限名称）
            
        Returns:
            (功能权限列表, 总数, 错误信息)
        """
        try:
            query = self.db.query(FeaturePermission)
            
            # 分类筛选
            if category:
                query = query.filter(FeaturePermission.category == category)
            
            # 状态筛选
            if status:
                query = query.filter(FeaturePermission.status == status)
            
            # 关键词搜索
            if keyword:
                query = query.filter(or_(
                    FeaturePermission.permission_key.like(f"%{keyword}%"),
                    FeaturePermission.permission_name.like(f"%{keyword}%")
                ))
            
            # 获取总数
            total = query.count()
            
            # 分页查询，按排序字段排序
            permissions = query.order_by(
                FeaturePermission.sort_order.asc(),
                FeaturePermission.id.asc()
            ).offset((page - 1) * size).limit(size).all()
            
            return permissions, total, None
            
        except Exception as e:
            logger.error(f"查询功能权限列表失败: {e}")
            return [], 0, f"查询功能权限列表失败: {str(e)}"
    
    def get_all_normal_permissions(self) -> List[FeaturePermission]:
        """
        获取所有正常状态的功能权限（不分页）
        
        Returns:
            功能权限列表
        """
        return self.db.query(FeaturePermission).filter(
            FeaturePermission.status == FeaturePermissionStatus.NORMAL.value
        ).order_by(
            FeaturePermission.sort_order.asc(),
            FeaturePermission.id.asc()
        ).all()
    
    def get_categories(self) -> List[str]:
        """
        获取所有权限分类
        
        Returns:
            分类列表
        """
        categories = self.db.query(FeaturePermission.category).filter(
            FeaturePermission.category.isnot(None),
            FeaturePermission.category != ""
        ).distinct().all()
        
        return [category[0] for category in categories if category[0]]

    def build_permissions_export_payload(
        self,
        permission_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        构建功能权限导出快照

        设计说明：
        - 导出统一基于前端勾选的 permission_key 列表，保证导出范围明确可控；
        - 文件结构使用稳定的 schema_version，后续如果要扩展字段，可以做到向后兼容；
        - 导出内容不包含数据库主键，避免不同服务器之间因自增 ID 不同导致导入污染。
        """
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
        missing_keys = [permission_key for permission_key in unique_permission_keys if permission_key not in found_keys]
        if missing_keys:
            missing_text = "、".join(missing_keys)
            logger.warning(f"构建功能权限导出快照失败，存在无效权限标识: {missing_text}")
            return None, f"以下权限不存在，无法导出: {missing_text}"

        snapshot_items = [
            FeaturePermissionSnapshotItem(
                permission_key=permission.permission_key,
                permission_name=permission.permission_name,
                description=permission.description,
                category=permission.category,
                icon=permission.icon,
                sort_order=permission.sort_order,
                status=permission.status
            )
            for permission in permissions
        ]

        payload = FeaturePermissionExportPayload(
            schema_version="feature_permissions.v1",
            exported_at=datetime.now(),
            total=len(snapshot_items),
            filters=FeaturePermissionExportFilter(
                page=1,
                size=len(snapshot_items),
                keyword="selected_permissions"
            ),
            permissions=snapshot_items
        )

        logger.info(
            "构建功能权限导出快照成功: "
            f"selected_count={len(unique_permission_keys)}, "
            f"export_count={len(snapshot_items)}, permission_keys={unique_permission_keys}"
        )
        return payload.model_dump(mode="json", exclude_none=True), None

    def import_permissions_from_payload(
        self,
        payload: FeaturePermissionExportPayload
    ) -> Tuple[Optional[Dict[str, int]], Optional[str]]:
        """
        从导出快照导入功能权限

        设计说明：
        - 导入统一按 permission_key 做幂等同步，适合同步到其他服务器；
        - 已存在的权限做更新，不存在的权限做创建，避免把“迁移权限列表”做成一次性脚本；
        - 不主动删除目标库多余权限，避免导入一个筛选后的文件时误删线上配置。
        """
        try:
            permission_items = payload.permissions
            duplicate_keys = self._find_duplicate_permission_keys(permission_items)
            if duplicate_keys:
                duplicate_text = "、".join(sorted(duplicate_keys))
                logger.warning(f"导入功能权限失败，文件内存在重复权限标识: {duplicate_text}")
                return None, f"导入文件中存在重复的权限标识: {duplicate_text}"

            created_count = 0
            updated_count = 0

            logger.info(
                "开始导入功能权限快照: "
                f"schema_version={payload.schema_version}, total_count={len(permission_items)}"
            )

            for item in permission_items:
                existing_permission = self.db.query(FeaturePermission).filter(
                    FeaturePermission.permission_key == item.permission_key
                ).first()

                if existing_permission:
                    logger.info(f"导入命中已有权限，准备更新: permission_key={item.permission_key}")
                    existing_permission.permission_name = item.permission_name
                    existing_permission.description = item.description
                    existing_permission.category = item.category
                    existing_permission.icon = item.icon
                    existing_permission.sort_order = item.sort_order
                    existing_permission.status = item.status
                    updated_count += 1
                    continue

                logger.info(f"导入命中新权限，准备创建: permission_key={item.permission_key}")
                self.db.add(
                    FeaturePermission(
                        permission_key=item.permission_key,
                        permission_name=item.permission_name,
                        description=item.description,
                        category=item.category,
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
        """
        更新卡密的功能权限
        
        Args:
            card_id: 卡密ID
            permission_keys: 权限标识列表
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            card = self.db.query(Card).filter(Card.id == card_id).first()
            
            if not card:
                return False, "卡密不存在"
            
            # 验证所有权限标识是否存在
            all_permissions = self.db.query(FeaturePermission).filter(
                FeaturePermission.permission_key.in_(permission_keys)
            ).all()
            
            found_keys = {p.permission_key for p in all_permissions}
            invalid_keys = set(permission_keys) - found_keys
            
            if invalid_keys:
                return False, f"以下权限标识不存在: {', '.join(invalid_keys)}"
            
            # 更新卡密的权限配置
            card.permissions = permission_keys
            self.db.commit()
            
            logger.info(f"更新卡密功能权限成功: card_id={card_id}, permissions={permission_keys}")
            return True, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新卡密功能权限失败: {e}")
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
        """
        获取卡密的功能权限标识列表
        
        Args:
            card_id: 卡密ID
            
        Returns:
            (权限标识列表, 错误信息)
        """
        try:
            card = self.db.query(Card).filter(Card.id == card_id).first()
            
            if not card:
                return [], "卡密不存在"
            
            # 从卡密的 permissions 字段获取权限标识
            permissions = card.permissions if isinstance(card.permissions, list) else []
            
            return permissions, None
            
        except Exception as e:
            logger.error(f"获取卡密功能权限失败: {e}")
            return [], f"获取卡密功能权限失败: {str(e)}"
