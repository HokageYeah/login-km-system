from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

    # 明确声明自增，避免迁移或不同数据库方言推断不一致时把主键建成非自增列。
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="功能权限ID")
    permission_key = Column(String(100), unique=True, nullable=False, index=True, comment="权限标识（如：wechat, ximalaya）")
    permission_name = Column(String(100), nullable=False, comment="权限名称（如：微信抓取、喜马拉雅播放）")
    # 这里把“权限分类”正式提升为应用归属字段。
    # 不引入中间关联表，是因为当前业务是“一条权限只属于一个应用”，直接外键最清晰也最易维护。
    # 历史数据仍可能为空，因此先允许为空，避免升级时把旧权限直接打坏。
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=True, index=True, comment="所属应用ID")
    description = Column(String(500), nullable=True, comment="权限描述")
    price = Column(Numeric(10, 2), default=0, nullable=False, comment="权限售卖价格")
    # category 保留为兼容历史导入导出和旧数据的展示字段，不再作为主分类依据。
    category = Column(String(50), nullable=True, comment="历史兼容分类字段")
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

    app = relationship("App", back_populates="feature_permissions")

    def __repr__(self):
        return (
            f"<FeaturePermission(id={self.id}, permission_key='{self.permission_key}', "
            f"permission_name='{self.permission_name}', app_id={self.app_id})>"
        )
