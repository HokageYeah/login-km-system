"""
应用服务层
处理应用管理相关的业务逻辑
"""
import secrets
from datetime import datetime
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.app import App, AppStatus
from app.core.logging_uru import logger


class AppService:
    """应用服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_app(
        self,
        app_name: str,
        app_key: Optional[str] = None
    ) -> Tuple[Optional[App], Optional[str]]:
        """
        创建应用
        
        Args:
            app_name: 应用名称
            app_key: 应用标识（可选，不提供则自动生成）
            
        Returns:
            (应用对象, 错误信息)
        """
        # 生成 app_key（如果未提供）
        if not app_key:
            app_key = self._generate_app_key(app_name)
        
        # 检查 app_key 是否已存在
        existing_app = self.db.query(App).filter(App.app_key == app_key).first()
        if existing_app:
            return None, "应用标识已存在"
        
        # 创建应用
        new_app = App(
            app_key=app_key,
            app_name=app_name,
            status=AppStatus.NORMAL
        )
        
        self.db.add(new_app)
        self.db.commit()
        self.db.refresh(new_app)
        
        logger.info(f"创建应用成功: {app_name} (app_key: {app_key})")
        
        return new_app, None
    
    def get_app_list(self) -> List[App]:
        """
        获取所有应用列表
        
        Returns:
            应用列表
        """
        return self.db.query(App).order_by(App.created_at.desc()).all()
    
    def get_app_by_id(self, app_id: int) -> Optional[App]:
        """
        根据ID获取应用
        
        Args:
            app_id: 应用ID
            
        Returns:
            应用对象
        """
        return self.db.query(App).filter(App.id == app_id).first()
    
    def get_app_by_key(self, app_key: str) -> Optional[App]:
        """
        根据app_key获取应用
        
        Args:
            app_key: 应用标识
            
        Returns:
            应用对象
        """
        return self.db.query(App).filter(App.app_key == app_key).first()
    
    def update_app_status(
        self,
        app_id: int,
        new_status: str
    ) -> Tuple[Optional[App], Optional[str]]:
        """
        更新应用状态
        
        Args:
            app_id: 应用ID
            new_status: 新状态（normal/disabled）
            
        Returns:
            (应用对象, 错误信息)
        """
        app = self.get_app_by_id(app_id)
        if not app:
            return None, "应用不存在"
        
        # 验证状态值
        try:
            status_enum = AppStatus(new_status)
        except ValueError:
            return None, "无效的状态值"
        
        old_status = app.status.value
        app.status = status_enum
        
        self.db.commit()
        self.db.refresh(app)
        
        logger.info(f"更新应用状态: {app.app_name} (ID: {app_id}), {old_status} -> {new_status}")
        
        return app, None
    
    def verify_app_available(self, app_key: str) -> Tuple[Optional[App], Optional[str]]:
        """
        验证应用是否可用
        
        Args:
            app_key: 应用标识
            
        Returns:
            (应用对象, 错误信息)
        """
        app = self.get_app_by_key(app_key)
        
        if not app:
            return None, "应用不存在"
        
        if app.status == AppStatus.DISABLED:
            return None, "应用已被禁用"
        
        return app, None
    
    def _generate_app_key(self, app_name: str) -> str:
        """
        生成应用标识
        
        Args:
            app_name: 应用名称
            
        Returns:
            生成的 app_key
            
        Format:
            app_name_prefix + random_suffix
            例如：wx_crawler_a8f3e9
        """
        # 将应用名称转为小写并替换空格为下划线
        prefix = app_name.lower().replace(' ', '_').replace('-', '_')
        
        # 只保留字母和数字
        prefix = ''.join(c for c in prefix if c.isalnum() or c == '_')
        
        # 限制前缀长度
        if len(prefix) > 20:
            prefix = prefix[:20]
        
        # 生成6位随机后缀
        suffix = secrets.token_hex(3)  # 3字节=6个十六进制字符
        
        return f"{prefix}_{suffix}"


def get_app_service(db: Session) -> AppService:
    """
    获取应用服务实例
    
    Args:
        db: 数据库会话
        
    Returns:
        AppService实例
    """
    return AppService(db)
