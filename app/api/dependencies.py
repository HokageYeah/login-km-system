"""
API 依赖函数
提供通用的依赖注入功能，如获取当前用户、验证权限等
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.sqlalchemy_db import get_sqlalchemy_db
from app.services.auth_service import AuthService
from app.models.user import UserRole

# HTTP Bearer Token 认证方案
security = HTTPBearer()


def get_db() -> Session:
    """
    获取数据库会话
    
    Returns:
        数据库会话
    """
    return get_sqlalchemy_db()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    获取当前登录用户信息
    
    Args:
        credentials: HTTP Bearer Token凭证
        db: 数据库会话
        
    Returns:
        用户信息字典
        
    Raises:
        HTTPException: 认证失败
    """
    token = credentials.credentials
    
    # 验证Token
    auth_service = AuthService(db)
    user_info, error = auth_service.verify_token(token)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info


async def get_current_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    获取当前管理员用户信息
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        管理员用户信息
        
    Raises:
        HTTPException: 权限不足
    """
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    获取当前用户信息（可选）
    如果没有提供Token或Token无效，返回None而不抛出异常
    
    Args:
        credentials: HTTP Bearer Token凭证
        db: 数据库会话
        
    Returns:
        用户信息字典或None
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
    # 验证Token
    auth_service = AuthService(db)
    user_info, error = auth_service.verify_token(token)
    
    if error:
        return None
    
    return user_info
