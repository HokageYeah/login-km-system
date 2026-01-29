"""
用户认证服务层
处理用户注册、登录、Token验证等业务逻辑
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from loguru import logger

from app.models.user import User, UserStatus, UserRole
from app.models.app import App, AppStatus
from app.models.user_token import UserToken
from app.models.user_card import UserCard, UserCardStatus
from app.utils.security import hash_password, verify_password, create_access_token
from app.core.config import settings
import colorama



class AuthService:
    """用户认证服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register(self, username: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        用户注册
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            (用户对象, 错误信息)，成功时错误信息为None
        """
        try:
            # 检查用户名是否已存在
            existing_user = self.db.query(User).filter(User.username == username).first()
            if existing_user:
                logger.warning(f"用户注册失败: 用户名已存在 - {username}")
                return None, "用户名已存在"
            
            # 创建新用户
            hashed_password = hash_password(password)
            new_user = User(
                username=username,
                password_hash=hashed_password,
                status=UserStatus.NORMAL,
                role=UserRole.USER
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            logger.info(f"用户注册成功: {username} (ID: {new_user.id})")
            return new_user, None
        except Exception as e:
            self.db.rollback()
            logger.error(f"用户注册异常: {username} - {str(e)}")
            return None, f"注册失败: {str(e)}"
    
    def login(
        self,
        username: str,
        password: str,
        app_key: str,
        device_id: str
    ) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            app_key: 应用标识
            device_id: 设备标识
            
        Returns:
            (token, 用户信息, 错误信息)
        """
        try:
            # 验证应用是否存在且有效
            app = self.db.query(App).filter(App.app_key == app_key).first()
            if not app:
                logger.warning(f"登录失败: 应用不存在 - {app_key}")
                return None, None, "应用不存在"
            if app.status == AppStatus.DISABLED:
                logger.warning(f"登录失败: 应用已被禁用 - {app_key}")
                return None, None, "应用已被禁用"
            
            # 验证用户名和密码
            user = self.db.query(User).filter(User.username == username).first()
            if not user:
                logger.warning(f"登录失败: 用户名不存在 - {username}")
                return None, None, "用户名或密码错误"
            
            if not verify_password(password, user.password_hash):
                logger.warning(f"登录失败: 密码错误 - {username}")
                return None, None, "用户名或密码错误"
            
            # 检查用户状态
            if user.status == UserStatus.BANNED:
                logger.warning(f"登录失败: 用户已被封禁 - {username}")
                return None, None, "用户已被封禁"
            
            # 更新最后登录时间
            user.last_login_at = datetime.now()
            
            # 生成JWT Token
            token_data = {
                "user_id": user.id,
                "username": user.username,
                "app_id": app.id,
                "device_id": device_id,
                "role": user.role.value
            }
            token = create_access_token(data=token_data)
            
            # 保存Token到数据库
            token_expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            user_token = UserToken(
                user_id=user.id,
                app_id=app.id,
                token=token,
                device_id=device_id,
                expire_time=token_expire
            )
            
            # 删除该用户在该应用该设备上的旧Token（如果存在）
            self.db.query(UserToken).filter(
                and_(
                    UserToken.user_id == user.id,
                    UserToken.app_id == app.id,
                    UserToken.device_id == device_id
                )
            ).delete()
            
            self.db.add(user_token)
            self.db.commit()
            
            # 检查用户是否已绑定卡密
            has_card = self._check_user_has_card(user.id)
            
            # 构造用户信息
            user_info = {
                "user_id": user.id,
                "username": user.username,
                "status": user.status.value,
                "role": user.role.value,
                "has_card": has_card
            }
            
            logger.info(f"用户登录成功: {username} (ID: {user.id}), 设备: {device_id}, 应用: {app_key}")
            return token, user_info, None
        except Exception as e:
            self.db.rollback()
            logger.error(f"用户登录异常: {username} - {str(e)}")
            return None, None, f"登录失败: {str(e)}"
    
    def verify_token(self, token: str) -> Tuple[Optional[dict], Optional[str]]:
        """
        验证Token
        
        Args:
            token: JWT Token
            
        Returns:
            (用户信息, 错误信息)
        """
        print(colorama.Fore.CYAN + f" [AuthService] 开始验证Token: {token[:20]}...")
        
        # 从数据库查询Token
        user_token = self.db.query(UserToken).filter(UserToken.token == token).first()
        if not user_token:
            print(colorama.Fore.RED + " [AuthService] Token不存在")
            return None, "Token无效"
        
        # 检查Token是否过期
        if user_token.expire_time < datetime.now():
            print(colorama.Fore.RED + f" [AuthService] Token已过期: {user_token.expire_time}")
            return None, "Token已过期"
        
        # 获取用户信息
        user = self.db.query(User).filter(User.id == user_token.user_id).first()
        if not user:
            print(colorama.Fore.RED + f" [AuthService] 用户不存在: user_id={user_token.user_id}")
            return None, "用户不存在"
        
        # 检查用户状态
        if user.status == UserStatus.BANNED:
            print(colorama.Fore.RED + f" [AuthService] 用户已被封禁: {user.username}")
            return None, "用户已被封禁"
            
        print(colorama.Fore.GREEN + f" [AuthService] 验证通过: {user.username}")
        
        # 构造用户信息
        user_info = {
            "user_id": user.id,
            "username": user.username,
            "status": user.status.value,
            "role": user.role.value,
            "app_id": user_token.app_id,
            "device_id": user_token.device_id
        }
        
        return user_info, None
    
    def logout(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        用户登出
        
        Args:
            token: JWT Token
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            # 获取Token信息用于日志
            user_token = self.db.query(UserToken).filter(UserToken.token == token).first()
            
            # 删除Token
            result = self.db.query(UserToken).filter(UserToken.token == token).delete()
            self.db.commit()
            
            if result > 0:
                if user_token:
                    logger.info(f"用户登出成功: user_id={user_token.user_id}, device={user_token.device_id}")
                return True, None
            
            logger.warning("登出失败: Token不存在")
            return False, "Token不存在"
        except Exception as e:
            self.db.rollback()
            logger.error(f"用户登出异常: {str(e)}")
            return False, f"登出失败: {str(e)}"
    
    def _check_user_has_card(self, user_id: int) -> bool:
        """
        检查用户是否已绑定有效卡密
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否有卡密
        """
        active_card = self.db.query(UserCard).filter(
            and_(
                UserCard.user_id == user_id,
                UserCard.status == UserCardStatus.ACTIVE
            )
        ).first()
        
        return active_card is not None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据用户ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            用户对象
        """
        return self.db.query(User).filter(User.username == username).first()


def get_auth_service(db: Session) -> AuthService:
    """
    获取认证服务实例
    
    Args:
        db: 数据库会话
        
    Returns:
        AuthService实例
    """
    return AuthService(db)
