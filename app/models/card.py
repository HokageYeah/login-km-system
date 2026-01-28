from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.sqlalchemy_db import Base


class CardStatus(str, enum.Enum):
    """卡密状态枚举"""
    UNUSED = "unused"
    USED = "used"
    DISABLED = "disabled"


class Card(Base):
    """卡密表模型"""
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True, comment="卡密ID")
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False, index=True, comment="所属应用ID")
    card_key = Column(String(100), unique=True, index=True, nullable=False, comment="卡密字符串")
    status = Column(
        SQLEnum(CardStatus),
        default=CardStatus.UNUSED,
        nullable=False,
        comment="卡密状态: unused-未使用, used-已使用, disabled-禁用"
    )
    expire_time = Column(DateTime, nullable=False, comment="过期时间")
    max_device_count = Column(Integer, default=1, nullable=False, comment="最大可绑定设备数")
    permissions = Column(JSON, nullable=True, comment="权限配置 JSON")
    remark = Column(String(255), nullable=True, comment="备注（套餐名称等）")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系映射
    app = relationship("App", back_populates="cards")
    user_cards = relationship("UserCard", back_populates="card", lazy="dynamic")
    card_devices = relationship("CardDevice", back_populates="card", lazy="dynamic")

    def __repr__(self):
        return f"<Card(id={self.id}, card_key='{self.card_key}', status='{self.status}')>"
