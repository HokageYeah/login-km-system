from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
import enum

from app.db.sqlalchemy_db import Base


class FeaturePermissionStatus(str, enum.Enum):
    """功能权限状态枚举"""
    NORMAL = "normal"
    DISABLED = "disabled"


class FeaturePermission(Base):
    """功能权限表模型
    
    用于配置系统中所有可用的功能权限（如：微信抓取、喜马拉雅播放等）
    这些功能权限可以被卡密引用，决定卡密能够使用哪些功能
    """
    __tablename__ = "feature_permissions"

    id = Column(Integer, primary_key=True, index=True, comment="功能权限ID")
    permission_key = Column(String(100), unique=True, nullable=False, index=True, comment="权限标识（如：wechat, ximalaya）")
    permission_name = Column(String(100), nullable=False, comment="权限名称（如：微信抓取、喜马拉雅播放）")
    description = Column(String(500), nullable=True, comment="权限描述")
    category = Column(String(50), nullable=True, comment="权限分类（如：数据抓取、媒体播放）")
    icon = Column(String(100), nullable=True, comment="图标")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序，数字越小越靠前")
    status = Column(
        String(20),
        default=FeaturePermissionStatus.NORMAL.value,
        nullable=False,
        comment="状态：normal-正常，disabled-禁用"
    )
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    def __repr__(self):
        return f"<FeaturePermission(id={self.id}, permission_key='{self.permission_key}', permission_name='{self.permission_name}')>"
