"""
安全工具模块
提供密码加密和JWT Token相关功能
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    生成密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        密码哈希值
        
    Note:
        bcrypt 限制密码最大长度为 72 字节，超出部分会被自动截断
    """
    # bcrypt 的限制是 72 字节，这里先截断密码以避免警告
    # 如果密码是 UTF-8 编码，一个中文字符可能占 3 字节
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        验证结果
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建JWT Token
    
    Args:
        data: 要编码的数据，通常包含 user_id, app_id, device_id 等
        expires_delta: 过期时间增量，如果不提供则使用默认配置
        
    Returns:
        JWT Token字符串
        
    Example:
        >>> token = create_access_token(
        ...     data={"user_id": 1, "app_id": 1, "device_id": "abc123"}
        ... )
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 生成JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解析JWT Token
    
    Args:
        token: JWT Token字符串
        
    Returns:
        解析后的数据字典，如果解析失败返回 None
        
    Raises:
        JWTError: Token无效或过期
        
    Example:
        >>> data = decode_access_token(token)
        >>> if data:
        ...     user_id = data.get("user_id")
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> bool:
    """
    验证Token是否有效
    
    Args:
        token: JWT Token字符串
        
    Returns:
        Token是否有效
    """
    payload = decode_access_token(token)
    return payload is not None


def get_token_expire_time(token: str) -> Optional[datetime]:
    """
    获取Token过期时间
    
    Args:
        token: JWT Token字符串
        
    Returns:
        过期时间，如果Token无效返回 None
    """
    payload = decode_access_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None
