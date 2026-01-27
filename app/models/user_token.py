from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.sqlalchemy_db import Base


class UserToken(Base):
    """用户Token表模型 - 用于登录会话管理"""
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True, comment="Token ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False, index=True, comment="应用ID")
    token = Column(String(500), unique=True, index=True, nullable=False, comment="JWT Token")
    device_id = Column(String(255), nullable=False, index=True, comment="设备标识")
    expire_time = Column(DateTime, nullable=False, comment="过期时间")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")

    # 关系映射
    user = relationship("User", back_populates="user_tokens")
    app = relationship("App", back_populates="user_tokens")

    # 联合索引：方便查询用户在特定应用和设备上的Token
    __table_args__ = (
        Index('idx_user_app_device', 'user_id', 'app_id', 'device_id'),
    )

    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, device_id='{self.device_id}')>"
