from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

# 获取当前环境
ENV = os.getenv("ENV", "development").lower()
print(f"当前环境: {ENV}")

# 对常见环境别名做统一映射，避免 Docker / CI 使用 production、development
# 这类更常见取值时退回到错误的默认配置文件。
ENV_ALIAS_MAP = {
    "prod": "prod",
    "production": "prod",
    "dev": "dev",
    "development": "dev",
    "test": "test",
}
normalized_env = ENV_ALIAS_MAP.get(ENV, ENV)

# 根据环境选择配置文件（老方法，根据文件名去拿文件配置，未使用dotenv库）以下使用dotenv库
# env_file = f".env.{ENV}" if os.path.exists(f".env.{ENV}") else ".env"
# 优先加载 .env 文件
env_file = ".env"
if normalized_env == "prod":
    env_file = ".env.production"
elif normalized_env == "test":
    env_file = ".env"
elif normalized_env == "dev":
    env_file = ".env.development"
print(f"加载配置文件: {env_file}")

# Docker、systemd、CI 这类部署场景通常会通过外部环境变量注入配置。
# 这里采用“外部环境优先，.env 文件兜底”的方式，既兼容本地开发，
# 也避免容器里已经注入的 DB_HOST、SECRET_KEY 被文件再次覆盖。
load_dotenv(env_file, override=False)

class Settings(BaseSettings):
    PROJECT_NAME: str = "通用卡密与授权系统" # 项目名称
    PROJECT_DESCRIPTION: str = "支持多应用的卡密授权管理系统API" # 项目描述
    PROJECT_VERSION: str = "1.0.0" # 项目版本
    API_PREFIX: str = "/api/v1" # 接口前缀
    # DATABASE_URL: str # 数据库连接字符串 暂时不配置
    DEBUG: bool = False # 是否为调试模式
    ENVIRONMENT: str # 环境变量
    VERSION: int = 1 # 版本号
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production-09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # docker 数据库字段
    MYSQL_ROOT_PASSWORD: Optional[str] = "aa123456"
    MYSQL_DATABASE: Optional[str] = "login_km_system_dev"
    MYSQL_USER: Optional[str] = "yy"
    MYSQL_PASSWORD: Optional[str] = "aa123456"


        # 数据库配置
    DB_DRIVER: Optional[str] = "mysql+mysqlconnector"
    DB_USER: Optional[str] = "root"
    DB_PASSWORD: Optional[str] = "aa123456"
    DB_HOST: Optional[str] = "localhost"
    DB_PORT: Optional[int] = 3306
    DB_NAME: Optional[str] = "login_km_system_dev"
    DB_CHARSET: Optional[str] = "utf8mb4"
    DB_ECHO: Optional[bool] = True
    DB_POOL_SIZE: Optional[int] = 5
    DB_MAX_OVERFLOW: Optional[int] = 10
    DB_POOL_RECYCLE: Optional[int] = 3600
    DB_POOL_TIMEOUT: Optional[int] = 30

    # @field_validator("DATABASE_URL")
    # def validate_database_url(cls, v: Optional[str]) -> Any:
    #     print('DATABASE_URL---', v)
    #     if not v:
    #         raise ValueError("DATABASE_URL must be provided")
    #     return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
