"""
创建管理员用户的脚本
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.sqlalchemy_db import get_sqlalchemy_db, database
from app.models.user import User, UserRole, UserStatus
from app.utils.security import hash_password
from loguru import logger


def create_admin_user(username: str = "admin", password: str = "admin123"):
    """
    创建管理员用户
    
    Args:
        username: 管理员用户名
        password: 管理员密码
    """
    database.connect()
    db = get_sqlalchemy_db()
    
    try:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        
        if existing_user:
            # 如果用户存在，更新为管理员角色
            if existing_user.role != UserRole.ADMIN:
                existing_user.role = UserRole.ADMIN
                db.commit()
                logger.info(f"用户 {username} 已存在，已更新为管理员角色")
            else:
                logger.info(f"管理员用户 {username} 已存在")
            return
        
        # 创建新的管理员用户
        hashed_password = hash_password(password)
        
        admin_user = User(
            username=username,
            password_hash=hashed_password,
            role=UserRole.ADMIN,
            status=UserStatus.NORMAL
        )
        
        db.add(admin_user)
        db.commit()
        
        logger.info(f"成功创建管理员用户: {username}")
        logger.info(f"登录密码: {password}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建管理员用户失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # 从命令行参数获取用户名和密码
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = "admin"
    
    if len(sys.argv) > 2:
        password = sys.argv[2]
    else:
        password = "admin123"
    
    create_admin_user(username, password)
    
    print("\n" + "="*50)
    print("管理员用户信息:")
    print(f"用户名: {username}")
    print(f"密码: {password}")
    print("="*50)
