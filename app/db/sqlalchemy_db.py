# src/sql/sql_connect_db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging
from app.config.database_config import get_database_config, DATABASE_URL
# 创建基类，用于声明模型
Base = declarative_base()

class Database:
    def __init__(self):
        self.db_config = get_database_config()
        self.db_url = DATABASE_URL
        self._engine = None
        self._session_factory = None

    def connect(self) -> None:
        """初始化数据库连接"""
        try:
            # 创建引擎，配置连接池
            self._engine = create_engine(
                self.db_url,
                poolclass=QueuePool,
                pool_size=self.db_config['pool_size'],
                max_overflow=self.db_config['max_overflow'],
                pool_timeout=self.db_config['pool_timeout'],
                pool_recycle=self.db_config['pool_recycle'],
                echo=self.db_config['echo']
            )
            
            # 创建会话工厂
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            )

            # 测试连接
            session = self._session_factory()
            try:
                session.execute(text("SELECT 1"))
                logging.info("sqlalchemy数据库连接成功")
            finally:
                session.close()

        except Exception as e:
            logging.error(f"sqlalchemy数据库连接失败: {e}")
            raise

    def get_session(self) -> Generator[Session, None, None]:
        """获取数据库会话"""
        if not self._session_factory:
            raise RuntimeError("sqlalchemy数据库未初始化，请先调用 connect()")
            
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

    def close(self) -> None:
        """关闭数据库连接"""
        if self._engine:
            self._engine.dispose()
            logging.info("sqlalchemy数据库连接已关闭")

# 创建全局数据库实例
database = Database()

# 获取数据库会话的工具函数
def get_sqlalchemy_db() -> Session:
    """
    获取数据库会话。

    注意：该函数主要给脚本或手动调用场景使用，调用方必须自行 close。
    FastAPI 接口依赖应使用 app.utils.dependencies.get_db 的 yield 版本，
    由框架在请求结束后统一释放连接。
    """
    if not database._session_factory:
        raise RuntimeError("sqlalchemy数据库未初始化，请先调用 connect()")

    try:
        return database._session_factory()
    except Exception as e:
        logging.error(f"获取数据库会话失败: {e}")
        raise
