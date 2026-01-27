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

9. **uvicorn**: 现代的ASGI服务器，用于运行FastAPI应用。

10. **cachetools**: 可以方便的进行缓存管理，可以减少数据库查询，提高接口响应速度。

11. **loguru**: 现代化的日志库，支持多种日志级别和格式，方便进行日志管理。

## 项目结构

```
.
├── alembic/              # 数据库迁移相关文件
│   ├── env.py           # Alembic环境配置
│   ├── script.py.mako   # 迁移脚本模板
│   └── versions/        # 迁移版本文件
├── app/                  # 应用程序代码
│   ├── api/              # API路由
│   │   ├── api.py       # API路由集合
│   │   └── endpoints/   # API端点
│   ├── config/           # 配置模块
│   │   └── database_config.py # 数据库配置
│   ├── core/             # 核心配置
│   │   ├── config.py    # 应用配置
│   │   └── logging.py   # 日志配置
│   ├── db/               # 数据库相关
│   │   └── sqlalchemy_db.py # SQLAlchemy数据库连接
│   │── decorators/       # 装饰器
│   │   └── cache_decorator.py # 缓存装饰器
│   ├── middleware/       # 中间件
│   │   └── exception_handlers.py # 异常处理器
│   ├── models/           # 数据库模型
│   │   └── article.py   # 文章模型
│   ├── schemas/          # Pydantic模型
│   │   └── wx_data.py   # 微信公众号数据验证模型
│   │   └── common_data.py   # 通用数据验证模型
│   ├── scripts/          # 脚本工具
│   │   ├── create_database.py # 创建数据库脚本
│   │   ├── init_database.py  # 初始化数据库脚本
│   │   ├── manage_db.py      # 使用alembic管理数据库脚本
│   │   ├── docker-entrypoint.sh # docker启动脚本
│   │   └── set_env.py        # 环境设置脚本
│   ├── services/         # 业务逻辑服务
│   │   └── wx_public.py # 微信公众号服务
│   ├── __init__.py      # 包初始化文件
│   └── main.py          # 应用入口
├── logs/                 # 日志文件目录
├── .env                  # 环境变量配置
├── .env.development      # 开发环境配置
├── .env.production       # 生产环境配置
├── .env.test             # 测试环境配置
├── alembic.ini           # Alembic配置
├── project_structure.sh  # 项目结构生成脚本
├── requirements.txt      # 项目依赖
├── run.sh                # 运行脚本
├── .gitignore            # git忽略文件
└── run_app.py            # 应用启动脚本
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

### 3. 环境配置

本项目支持多环境配置，包括：

- `.env`：默认环境配置
- `.env.development`：开发环境配置
- `.env.test`：测试环境配置
- `.env.production`：生产环境配置

编辑相应的环境配置文件，设置数据库连接信息和其他参数：

```
# 数据库配置
DB_DRIVER=mysql+mysqlconnector
DB_USER=root
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=wx_public_dev
DB_CHARSET=utf8mb4

# API配置
API_PREFIX=/api/v1
DEBUG=True
ENVIRONMENT=development
```

### 4. 数据库操作

#### 4.1 创建数据库

在使用应用前，需要先创建数据库。可以使用`app/scripts/create_database.py`脚本：

```bash
python -m app.scripts.create_database
或者
python -m app.scripts.set_env dev create_db
```

该脚本会根据环境配置文件中的数据库设置创建数据库。

#### 4.2 初始化数据库表

创建数据库后，需要初始化数据库表结构。有两种方式：

**方式一：使用SQLAlchemy直接创建表**

```bash
python -m app.scripts.init_database
```

该脚本会使用SQLAlchemy的`create_all()`方法创建所有在`app/models`目录下定义的模型对应的表。

**方式二：使用Alembic进行数据库迁移（推荐）**

```bash
# 创建迁移脚本
alembic revision --autogenerate -m "创建初始表结构"

# 应用迁移
alembic upgrade head
```
> 或者使用set_env.py脚本去管理数据库，创建迁移脚本，应用迁移，回滚迁移。内部使用manage_db.py脚本调用alembic命令

```bash
# 创建迁移脚本
python -m app.scripts.set_env dev migrate revision --autogenerate -m "pro_table"

# 应用迁移
python -m app.scripts.set_env dev upgrade

# 回滚迁移
python -m app.scripts.set_env dev downgrade
```

#### 4.3 数据库字段更新

> 当模型定义发生变化时（如添加、修改或删除字段），使用Alembic进行数据库迁移：

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "更新字段描述"

# 应用迁移
alembic upgrade head

# 回滚迁移（如需要）
alembic downgrade -1  # 回滚一个版本
```
> 或者使用set_env.py脚本去管理数据库，创建迁移脚本，应用迁移，回滚迁移。内部使用manage_db.py脚本调用alembic命令

```bash
# 创建迁移脚本
python -m app.scripts.set_env dev migrate revision --autogenerate -m "pro_table"

# 应用迁移
python -m app.scripts.set_env dev upgrade

# 回滚迁移
python -m app.scripts.set_env dev downgrade
```

Alembic会自动检测模型变化并生成相应的迁移脚本，然后可以应用或回滚这些变化。

### 5. 运行应用

有两种方式运行应用：

**方式一：使用run.sh脚本（推荐）**

```bash
./run.sh
```

该脚本会自动创建虚拟环境、安装依赖并启动应用。脚本内容如下：

```bash
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
python run_app.py
```

**方式二：直接运行Python脚本**

```bash
python run_app.py
```

`run_app.py`脚本会确保项目根目录被添加到Python路径中，以便正确导入应用模块：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 添加项目根目录到python的路径
import os
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

if __name__ == "__main__":
    from app.main import app
    import uvicorn
    import logging
    
    logging.info("启动应用服务器...")
    uvicorn.run("app.main:app", host="localhost", port=8002, reload=True)
```

应用将在 http://localhost:8002 运行，API文档可在 http://localhost:8002/docs 访问。

## API接口

### 搜索微信公众号文章

```
GET /api/v1/wx/search?query=关键词
```

此接口会调用搜狗微信搜索，获取相关的微信公众号文章信息。

## 日志系统

本项目集成了完善的日志系统，支持控制台彩色输出和文件记录：

- **日志配置**：在`app/core/logging.py`中配置
- **日志级别**：根据DEBUG环境变量自动调整（DEBUG模式下为DEBUG级别，否则为INFO级别）
- **日志格式**：包含时间、日志名称、级别和消息，不同级别使用不同颜色显示
- **日志输出**：同时输出到控制台和`logs`目录下的日期命名文件（如`app_2025-05-16.log`）

## 环境隔离与切换

### Python虚拟环境

本项目使用Python虚拟环境进行环境隔离，确保项目依赖不会影响系统全局Python环境。虚拟环境的创建和激活方法如下：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# 在Linux/macOS上
source venv/bin/activate
# 在Windows上
venv\Scripts\activate
```

### python-dotenv环境切换

本项目使用python-dotenv库实现不同环境（开发、测试、生产）的配置隔离和切换。环境切换的实现方式如下：

1. **环境配置文件**：
   - `.env`：默认环境配置
   - `.env.development`：开发环境配置
   - `.env.test`：测试环境配置
   - `.env.production`：生产环境配置

2. **环境切换机制**：
   在`app/core/config.py`中，通过设置`ENV`环境变量来切换不同的环境配置：

   ```python
   # 获取当前环境
   ENV = os.getenv("ENV", "development")
   
   # 根据环境选择配置文件
   env_file = ".env"
   if ENV == "prod":
       env_file = ".env.production"
   elif ENV == "test":
       env_file = ".env"
   elif ENV == "dev":
       env_file = ".env.development"
       
   # 加载环境配置
   load_dotenv(env_file, override=True)
   ```
    使用：
    ```bash
    python -m app.scripts.set_env dev
    或者
    python -m app.scripts.set_env test
    或者
    python -m app.scripts.set_env prod
    ```

3. **切换环境的方法**：
   - 通过设置环境变量：`export ENV=prod`（Linux/macOS）或`set ENV=prod`（Windows）
   - 通过脚本设置：在`app/scripts/set_env.py`中可以编程方式设置环境
   - 在运行脚本中设置：如`os.environ["ENV"] = "production"`

## 许可证

MIT
