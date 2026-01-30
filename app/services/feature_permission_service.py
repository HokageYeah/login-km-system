"""
功能权限服务层
提供功能权限的增删改查以及卡密权限关联管理
"""
from typing import List, Tuple, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_
from loguru import logger

from app.models.feature_permission import FeaturePermission, FeaturePermissionStatus
from app.models.card import Card


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
