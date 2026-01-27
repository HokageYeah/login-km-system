from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.sqlalchemy_db import Base


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    NORMAL = "normal"
    BANNED = "banned"


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """用户表模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(100), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    status = Column(
        SQLEnum(UserStatus),
        default=UserStatus.NORMAL,
        nullable=False,
        comment="用户状态: normal-正常, banned-封禁"
    )
    role = Column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False,
        comment="用户角色: user-普通用户, admin-管理员"
    )
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系映射
    user_cards = relationship("UserCard", back_populates="user", lazy="dynamic")
    user_tokens = relationship("UserToken", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', status='{self.status}')>"
