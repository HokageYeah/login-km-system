from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.sqlalchemy_db import Base


class CardDeviceStatus(str, enum.Enum):
    """设备绑定状态枚举"""
    ACTIVE = "active"
    DISABLED = "disabled"


class CardDevice(Base):
    """卡密-设备绑定表模型"""
    __tablename__ = "card_devices"

    id = Column(Integer, primary_key=True, index=True, comment="绑定ID")
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, index=True, comment="卡密ID")
    device_id = Column(String(255), nullable=False, index=True, comment="设备唯一标识")
    device_name = Column(String(255), nullable=True, comment="设备名称")
    bind_time = Column(DateTime, default=func.now(), nullable=False, comment="绑定时间")
    last_active_at = Column(DateTime, default=func.now(), nullable=False, comment="最后活跃时间")
    status = Column(
        SQLEnum(CardDeviceStatus),
        default=CardDeviceStatus.ACTIVE,
        nullable=False,
        comment="设备状态: active-激活, disabled-禁用"
    )
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系映射
    card = relationship("Card", back_populates="card_devices")

    # 唯一索引：一个卡密不能重复绑定同一设备
    __table_args__ = (
        Index('idx_card_device', 'card_id', 'device_id', unique=True),
    )

    def __repr__(self):
        return f"<CardDevice(id={self.id}, card_id={self.card_id}, device_id='{self.device_id}', status='{self.status}')>"
