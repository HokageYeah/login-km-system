from sqlalchemy import Column, Integer, DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.sqlalchemy_db import Base


class UserCardStatus(str, enum.Enum):
    """用户卡密绑定状态枚举"""
    ACTIVE = "active"
    UNBIND = "unbind"


class UserCard(Base):
    """用户-卡密绑定表模型"""
    __tablename__ = "user_cards"

    id = Column(Integer, primary_key=True, index=True, comment="绑定ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, index=True, comment="卡密ID")
    bind_time = Column(DateTime, default=func.now(), nullable=False, comment="绑定时间")
    status = Column(
        SQLEnum(UserCardStatus),
        default=UserCardStatus.ACTIVE,
        nullable=False,
        comment="绑定状态: active-激活, unbind-解绑"
    )
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系映射
    user = relationship("User", back_populates="user_cards")
    card = relationship("Card", back_populates="user_cards")

    # 唯一索引：一个用户不能重复绑定同一张卡密
    __table_args__ = (
        Index('idx_user_card', 'user_id', 'card_id', unique=True),
    )

    def __repr__(self):
        return f"<UserCard(id={self.id}, user_id={self.user_id}, card_id={self.card_id}, status='{self.status}')>"
