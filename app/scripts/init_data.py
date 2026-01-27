"""
初始化系统数据
创建默认应用和管理员账户
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from sqlalchemy.orm import Session
from app.db.sqlalchemy_db import database, Base
from app.models.app import App, AppStatus
from app.models.user import User, UserStatus, UserRole
from app.utils.security import hash_password
from datetime import datetime


def init_default_data():
    """初始化默认数据"""
    
    # 连接数据库
    database.connect()
    db: Session = next(database.get_session())
    
    try:
        print("=" * 60)
        print("开始初始化系统数据...")
        print("=" * 60)
        
        # 1. 创建默认应用
        print("\n1. 检查默认应用...")
        default_app = db.query(App).filter(App.app_key == "default_app").first()
        
        if not default_app:
            default_app = App(
                app_key="default_app",
                app_name="默认应用",
                status=AppStatus.NORMAL
            )
            db.add(default_app)
            db.commit()
            db.refresh(default_app)
            print(f"   ✓ 创建默认应用成功")
            print(f"     - 应用ID: {default_app.id}")
            print(f"     - 应用Key: {default_app.app_key}")
            print(f"     - 应用名称: {default_app.app_name}")
        else:
            print(f"   ✓ 默认应用已存在 (ID: {default_app.id})")
        
        # 2. 创建管理员账户
        print("\n2. 检查管理员账户...")
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            admin_password = "admin123456"  # 默认密码
            admin_user = User(
                username="admin",
                password_hash=hash_password(admin_password),
                status=UserStatus.NORMAL,
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"   ✓ 创建管理员账户成功")
            print(f"     - 用户ID: {admin_user.id}")
            print(f"     - 用户名: {admin_user.username}")
            print(f"     - 默认密码: {admin_password}")
            print(f"     ⚠️  请在首次登录后立即修改密码！")
        else:
            print(f"   ✓ 管理员账户已存在 (ID: {admin_user.id})")
        
        # 3. 创建测试普通用户
        print("\n3. 检查测试用户...")
        test_user = db.query(User).filter(User.username == "testuser").first()
        
        if not test_user:
            test_password = "test123456"  # 默认密码
            test_user = User(
                username="testuser",
                password_hash=hash_password(test_password),
                status=UserStatus.NORMAL,
                role=UserRole.USER
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"   ✓ 创建测试用户成功")
            print(f"     - 用户ID: {test_user.id}")
            print(f"     - 用户名: {test_user.username}")
            print(f"     - 默认密码: {test_password}")
        else:
            print(f"   ✓ 测试用户已存在 (ID: {test_user.id})")
        
        print("\n" + "=" * 60)
        print("系统数据初始化完成！")
        print("=" * 60)
        
        print("\n📋 账户信息汇总：")
        print("-" * 60)
        print(f"管理员账户：")
        print(f"  用户名: admin")
        print(f"  密码: admin123456")
        print(f"\n测试账户：")
        print(f"  用户名: testuser")
        print(f"  密码: test123456")
        print(f"\n应用标识：")
        print(f"  app_key: default_app")
        print("-" * 60)
        
        print("\n🚀 可以开始使用系统了！")
        print("   1. 启动服务: python run_app.py")
        print("   2. 访问文档: http://localhost:8002/docs")
        print("   3. 使用上述账户进行登录测试")
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        database.close()


if __name__ == "__main__":
    init_default_data()
