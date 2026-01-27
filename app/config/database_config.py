import os
from typing import Dict, Any
from dotenv import load_dotenv
from app.core.config import settings

# 获取当前环境变量，默认为开发环境
def get_database_config():
    """根据当前环境获取数据库配置"""
    env = os.getenv("ENV", "development").lower()
    print("\n当前数据库环境信息:")
    print("----------------------------------------")
    print(f"database_config.py---- ENV: {env}") # 系统环境变量
    print(f"database_config.py---- DB_NAME: {os.getenv('DB_NAME')}") 
    print(f"database_config.py---- settings.DB_NAME: {settings.DB_NAME}") 
    print(f"database_config.py---- settings.DB_CHARSET: {settings.Config.env_file}") 
    print("----------------------------------------")
    return {
        "driver": settings.DB_DRIVER,
        "username": settings.DB_USER,
        "password": settings.DB_PASSWORD,
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "database": settings.DB_NAME,
        "charset": settings.DB_CHARSET,
        "echo": settings.DB_ECHO,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_timeout": settings.DB_POOL_TIMEOUT,

    }


def get_database_url() -> str:
    """获取当前环境的数据库URL"""
    config = get_database_config()
    return f"{config['driver']}://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"

# 导出数据库URL供SQLAlchemy和Alembic使用
DATABASE_URL = get_database_url()
