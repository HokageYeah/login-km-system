from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.sqlalchemy_db import Base


class AppStatus(str, enum.Enum):
    """应用状态枚举"""
    NORMAL = "normal"
    DISABLED = "disabled"


class App(Base):
    """应用表模型"""
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True, comment="应用ID")
    app_key = Column(String(100), unique=True, index=True, nullable=False, comment="应用唯一标识")
    app_name = Column(String(100), nullable=False, comment="应用名称")
    status = Column(
        SQLEnum(AppStatus),
        default=AppStatus.NORMAL,
        nullable=False,
        comment="应用状态: normal-正常, disabled-禁用"
    )
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系映射
    cards = relationship("Card", back_populates="app", lazy="dynamic")
    user_tokens = relationship("UserToken", back_populates="app", lazy="dynamic")

    def __repr__(self):
        return f"<App(id={self.id}, app_key='{self.app_key}', app_name='{self.app_name}')>"
