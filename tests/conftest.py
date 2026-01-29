"""
Pytest 配置文件
提供测试夹具(fixtures)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.sqlalchemy_db import Base, get_sqlalchemy_db
from app.core.config import settings


# 创建测试数据库引擎
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """数据库会话夹具"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 测试结束后删除所有表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """测试客户端夹具"""
    # 注意：由于使用内存数据库和TestClient，依赖注入可能需要特殊处理
    # 这里使用简单的TestClient
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_app():
    """获取应用实例"""
    from app.models.app import App, AppStatus
    from app.db.sqlalchemy_db import get_sqlalchemy_db
    
    db = get_sqlalchemy_db()
    
    # 检查是否已存在测试应用
    existing_app = db.query(App).filter(App.app_key == "test_app").first()
    if existing_app:
        return existing_app
    
    # 创建测试应用
    app = App(
        app_key="test_app",
        app_name="测试应用",
        status=AppStatus.NORMAL
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    
    return app


@pytest.fixture(scope="function")
def test_user(db_session, test_app):
    """创建测试用户"""
    from app.models.user import User, UserStatus, UserRole
    from app.utils.security import hash_password
    
    user = User(
        username="testuser",
        password_hash=hash_password("testpass123"),
        status=UserStatus.NORMAL,
        role=UserRole.USER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture(scope="function")
def test_admin(db_session, test_app):
    """创建测试管理员"""
    from app.models.user import User, UserStatus, UserRole
    from app.utils.security import hash_password
    
    admin = User(
        username="testadmin",
        password_hash=hash_password("adminpass123"),
        status=UserStatus.NORMAL,
        role=UserRole.ADMIN
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    return admin
