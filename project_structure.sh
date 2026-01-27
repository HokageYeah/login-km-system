#!/bin/bash

# 创建项目目录结构
mkdir -p app/api/endpoints
mkdir -p app/core
mkdir -p app/db
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/services
mkdir -p alembic

# 创建主要文件

# .env文件
cat > .env << 'EOL'
DATABASE_URL=mysql+mysqlconnector://user:password@localhost:3306/wx_public
API_PREFIX=/api/v1
DEBUG=True
ENVIRONMENT=development
EOL

# 主应用文件
cat > app/main.py << 'EOL'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.api import api_router

app = FastAPI(
    title="微信公众号爬虫",
    description="用于爬取微信公众号资源的API",
    version="0.1.0",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加路由
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {"message": "微信公众号爬虫API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
EOL

# 配置文件
cat > app/core/config.py << 'EOL'
from typing import Any, Dict, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_PREFIX: str = "/api/v1"
    DATABASE_URL: str
    DEBUG: bool = False
    ENVIRONMENT: str

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: Optional[str]) -> Any:
        if not v:
            raise ValueError("DATABASE_URL must be provided")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
EOL

# 数据库连接
cat > app/db/session.py << 'EOL'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOL

# 数据库初始化
cat > app/db/init_db.py << 'EOL'
from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.models import article


def init_db() -> None:
    # 创建数据库表
    Base.metadata.create_all(bind=engine)


def init_data(db: Session) -> None:
    # 初始化数据
    pass
EOL

# 文章模型
cat > app/models/article.py << 'EOL'
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.session import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    author = Column(String(100))
    public_account = Column(String(100))
    content = Column(Text)
    url = Column(String(255))
    publish_date = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
EOL

# 模型导出
cat > app/models/__init__.py << 'EOL'
from app.models.article import Article
EOL

# 文章Schema
cat > app/schemas/article.py << 'EOL'
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ArticleBase(BaseModel):
    title: str
    author: Optional[str] = None
    public_account: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    publish_date: Optional[str] = None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(ArticleBase):
    title: Optional[str] = None


class ArticleInDBBase(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Article(ArticleInDBBase):
    pass
EOL

# Schema导出
cat > app/schemas/__init__.py << 'EOL'
from app.schemas.article import Article, ArticleCreate, ArticleUpdate
EOL

# 微信公众号服务
cat > app/services/wx_public.py << 'EOL'
import httpx
from fastapi import HTTPException


async def fetch_wx_articles(query: str):
    """获取微信公众号文章"""
    url = f"https://weixin.sogou.com/weixin?type=2&s_from=input&query={query}&ie=utf8&_sug_=n&_sug_type_="
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.text,
                "url": url
            }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")
EOL

# API路由
cat > app/api/endpoints/wx_public.py << 'EOL'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.wx_public import fetch_wx_articles

router = APIRouter()


@router.get("/search")
async def search_wx_articles(query: str = Query(..., description="搜索关键词")):
    """搜索微信公众号文章"""
    result = await fetch_wx_articles(query)
    return result
EOL

# API路由集合
cat > app/api/api.py << 'EOL'
from fastapi import APIRouter

from app.api.endpoints import wx_public

api_router = APIRouter()
api_router.include_router(wx_public.router, prefix="/wx", tags=["微信公众号"])
EOL

# 初始化文件
cat > app/__init__.py << 'EOL'
# 应用初始化
EOL

# Alembic配置
cat > alembic.ini << 'EOL'
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# see https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
# for all available tokens
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to alembic/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "version_path_separator" below.
# version_locations = %(here)s/bar:%(here)s/bat:alembic/versions

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses os.pathsep.
# If this key is omitted entirely, it falls back to the legacy behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os  # Use os.pathsep. Default configuration used for new projects.

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = driver://user:pass@localhost/dbname

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOL

# Alembic环境配置
mkdir -p alembic/versions
cat > alembic/env.py << 'EOL'
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.db.session import Base
from app.models import article
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOL

# Alembic脚本模板
cat > alembic/script.py.mako << 'EOL'
"""\${message}

Revision ID: \${up_revision}
Revises: \${down_revision | comma,n}
Create Date: \${create_date}

"""
from alembic import op
import sqlalchemy as sa
\${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = \${repr(up_revision)}
down_revision = \${repr(down_revision)}
branch_labels = \${repr(branch_labels)}
depends_on = \${repr(depends_on)}


def upgrade() -> None:
    \${upgrades if upgrades else "pass"}


def downgrade() -> None:
    \${downgrades if downgrades else "pass"}
EOL

# README文件
cat > README.md << 'EOL'
# 微信公众号爬虫

这是一个用于爬取微信公众号资源的Python项目。

## 集成框架

本项目集成了以下框架和库：

1. **FastAPI**: 现代、快速的Web框架，用于构建API。它基于标准的Python类型提示，提供自动文档生成和高性能。

2. **SQLAlchemy**: Python的SQL工具包和ORM框架，提供了SQL抽象层，使得数据库操作更加简单和灵活。

3. **Alembic**: SQLAlchemy的数据库迁移工具，用于管理数据库模式的变更。

4. **MySQL**: 用于数据存储的关系型数据库。

5. **python-dotenv**: 用于从.env文件加载环境变量，方便配置管理。

6. **pydantic-settings**: 基于pydantic的配置管理工具，提供类型安全的配置验证。

7. **pydantic**: 数据验证和设置管理库，使用Python类型注解。

8. **httpx**: 现代化的HTTP客户端，支持异步请求，用于爬取网页内容。

## 项目结构

```
.
├── alembic/              # 数据库迁移相关文件
├── app/                  # 应用程序代码
│   ├── api/              # API路由
│   │   └── endpoints/    # API端点
│   ├── core/             # 核心配置
│   ├── db/               # 数据库相关
│   ├── models/           # 数据库模型
│   ├── schemas/          # Pydantic模型
│   └── services/         # 业务逻辑服务
├── .env                  # 环境变量配置
├── alembic.ini           # Alembic配置
└── requirements.txt      # 项目依赖
```

## 安装和运行

### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

编辑`.env`文件，设置数据库连接信息：

```
DATABASE_URL=mysql+mysqlconnector://user:password@localhost:3306/wx_public
```

### 4. 初始化数据库

```bash
alembic upgrade head
```

### 5. 运行应用

```bash
uvicorn app.main:app --reload
```

应用将在 http://localhost:8000 运行，API文档可在 http://localhost:8000/docs 访问。

## API接口

### 搜索微信公众号文章

```
GET /api/v1/wx/search?query=关键词
```

此接口会调用搜狗微信搜索，获取相关的微信公众号文章信息。

## 环境隔离

本项目使用Python虚拟环境进行环境隔离，确保项目依赖不会影响系统全局Python环境。

## 许可证

MIT
EOL

# 启动脚本
cat > run.sh << 'EOL'
#!/bin/bash

# 创建并激活虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 运行应用
echo "启动应用..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOL

# 使脚本可执行
chmod +x run.sh
chmod +x project_structure.sh

echo "项目结构创建完成！"
echo "请执行 ./project_structure.sh 创建项目结构"
echo "然后执行 ./run.sh 启动应用"