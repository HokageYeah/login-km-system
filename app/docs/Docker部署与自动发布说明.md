# Docker 部署与自动发布说明

本文档是当前项目**唯一权威的部署主文档**，用于说明真实生效的 Docker 打包、容器启动、数据库迁移、前端 Nginx 代理以及 GitHub Actions 自动发布流程。

后续如果任务涉及以下任一方向，必须优先参考本文档，而不是凭经验假设或继续查找旧文档：

- Docker 打包失败
- Linux 服务器 Docker 部署异常
- `docker compose` 流程优化
- 镜像构建阶段代理问题
- 容器启动后数据库迁移问题
- 前端 Nginx 代理问题
- GitHub Actions 自动发布问题

## 一、当前部署架构总览

当前项目采用 **三服务 Docker Compose 编排**：

- `mysql`：MySQL 8.0，负责业务数据持久化
- `backend`：FastAPI 后端，负责授权裁决、后台管理、API 输出
- `frontend`：Vue 管理后台构建产物，通过 Nginx 提供静态页面，并代理 `/api`、`/docs`、`/redoc`

整体关系如下：

```text
GitHub Push / 手工部署
        ↓
docker compose build
        ↓
┌─────────────┬─────────────┬─────────────┐
│    mysql    │   backend   │  frontend   │
│   数据库     │   FastAPI   │ Nginx + SPA │
└─────────────┴─────────────┴─────────────┘
        ↑              ↑              │
        └──── backend 等待 DB 就绪 ────┘
                       │
              Alembic 自动迁移
```

## 二、权威文件清单

当前 Docker 与自动部署链路以以下文件为准：

- 编排入口：
  - `docker-compose.yml`
- 后端镜像与启动脚本：
  - `docker/backend/Dockerfile`
  - `docker/backend/docker-entrypoint.sh`
- 前端镜像与代理配置：
  - `docker/frontend/Dockerfile`
  - `docker/frontend/nginx.conf`
- 自动发布工作流：
  - `.github/workflows/deploy.yml`
- Docker 部署环境文件：
  - `.env.docker`
- 应用业务环境文件：
  - `.env.production`
  - `.env.development`
  - `.env.test`

如果本文档描述与以上真实文件冲突，以真实文件为准；如果真实文件已经确认调整完成，应同步回写本文档。

## 三、部署前提与环境准备

在当前部署主线下，建议至少满足以下条件：

- Linux 服务器已安装可用的 Docker 与 Docker Compose
- 服务器具备足够的磁盘空间，用于镜像构建、容器运行、MySQL 数据卷持久化
- 服务器网络能够访问：
  - Docker Hub
  - PyPI
  - npm Registry
- 如果服务器网络受限，需要提前准备好宿主机代理，并在 `.env.docker` 中显式配置 `KM_DOCKER_*`

部署前至少确认以下文件和配置存在：

- `.env.docker`
- `.env.production` 或其他目标应用环境文件
- 目标数据库配置、密钥配置、端口策略已经按目标环境设置完成

如果是首次部署，建议先做一轮最小化检查：

- `SECRET_KEY` 已改为强随机值
- `DEBUG=False`
- 数据库密码不是弱口令
- `KM_APP_ENV_FILE` 指向正确环境文件
- 是否需要 `KM_AUTO_INIT_DATA` 已明确

## 四、docker-compose.yml 的真实流程

### 4.1 `mysql` 服务

`mysql` 服务使用 `mysql:8.0` 镜像，特点如下：

- 通过 `.env.docker` 注入 MySQL 初始化环境变量
- 使用 `mysql_data` volume 做数据持久化
- 设置了字符集和排序规则：
  - `utf8mb4`
  - `utf8mb4_unicode_ci`
- 配置了健康检查：
  - 使用 `mysqladmin ping` 判断是否可用

这意味着：

- `backend` 不会在数据库未就绪时立即启动业务主流程
- 当前容器编排不是“靠睡眠时间碰运气”，而是基于健康检查 + 启动脚本双重等待

### 4.2 `backend` 服务

`backend` 服务由 `docker/backend/Dockerfile` 构建，关键特点：

- 构建上下文是项目根目录
- 构建时显式使用：
  - `build.network: host`
  - `build.extra_hosts: host.docker.internal:host-gateway`
- 构建参数支持代理：
  - `KM_DOCKER_HTTP_PROXY`
  - `KM_DOCKER_HTTPS_PROXY`
  - `KM_DOCKER_ALL_PROXY`
  - `KM_DOCKER_NO_PROXY`

运行时的环境变量来源分两层：

1. `.env.docker`
   负责部署层配置，例如：
   - 代理
   - MySQL 初始化参数
   - 时区
   - `KM_APP_ENV_FILE`
   - `KM_AUTO_INIT_DATA`

2. `${KM_APP_ENV_FILE:-.env.production}`
   负责应用业务层配置，例如：
   - `DB_*`
   - `SECRET_KEY`
   - `DEBUG`
   - `API_PREFIX`

也就是说，当前 Docker 部署并不是把所有配置都堆在 `.env.docker`，而是通过 `KM_APP_ENV_FILE` 决定 backend 容器最终加载哪套应用配置。

### 4.3 `frontend` 服务

`frontend` 服务由 `docker/frontend/Dockerfile` 构建，关键特点：

- 使用 Node 20 Alpine 做构建阶段
- 使用 Nginx 1.27 Alpine 做运行阶段
- 构建阶段也支持代理参数
- 构建阶段设置 `NODE_OPTIONS=--max-old-space-size=1536`

这个内存限制的目的不是提速，而是：

- 降低 `vue-tsc -b && vite build` 在小内存 Linux 服务器上被 OOM Killer 杀掉的概率
- 提高自动部署时前端构建成功率

## 五、环境变量与配置分层

当前部署方案采用“部署层配置”和“应用层配置”分离的方式。

### 5.1 `.env.docker` 的职责

`.env.docker` 负责 Docker / Compose 层参数，例如：

- MySQL 容器初始化参数
- 构建代理与运行代理
- `KM_APP_ENV_FILE`
- `KM_AUTO_INIT_DATA`

### 5.2 应用环境文件的职责

应用环境文件例如：

- `.env.production`
- `.env.development`
- `.env.test`

主要负责业务配置，例如：

- `DB_*`
- `SECRET_KEY`
- `DEBUG`
- `API_PREFIX`

### 5.3 `KM_APP_ENV_FILE` 的作用

`backend` 服务在 `docker-compose.yml` 中会按下面顺序读取环境文件：

1. `.env.docker`
2. `${KM_APP_ENV_FILE:-.env.production}`

因此：

- Docker Compose 必须先读到 `.env.docker`
- `.env.docker` 中的 `KM_APP_ENV_FILE` 决定 backend 容器最终注入哪套应用环境

常见示例：

```env
KM_APP_ENV_FILE=.env.production
```

### 5.4 代理变量的使用建议

如服务器不需要代理，可以保持为空：

```env
KM_DOCKER_HTTP_PROXY=
KM_DOCKER_HTTPS_PROXY=
KM_DOCKER_ALL_PROXY=
KM_DOCKER_NO_PROXY=localhost,127.0.0.1,::1,mysql
```

如服务器需要经过宿主机代理访问外网，可按实际环境填写，例如：

```env
KM_DOCKER_HTTP_PROXY=http://host.docker.internal:8118
KM_DOCKER_HTTPS_PROXY=http://host.docker.internal:8118
KM_DOCKER_ALL_PROXY=socks5://host.docker.internal:1080
KM_DOCKER_NO_PROXY=localhost,127.0.0.1,::1,mysql
```

注意：

- 不要机械照抄其他机器的代理地址
- 代理地址必须是 Docker 构建阶段和容器运行阶段都能访问到的地址
- 如果代理服务就在 Linux 宿主机本机，当前编排已通过 `build.network: host` 和 `host.docker.internal` 映射尽量兼容这种场景

## 六、后端镜像构建与启动细节

### 6.1 docker/backend/Dockerfile

后端镜像构建流程：

1. 基于 `python:3.11-slim`
2. 接收可选代理 ARG
3. 转换为标准代理环境变量
4. `COPY requirements.txt`
5. 执行 `pip install -r requirements.txt`
6. `COPY . .`
7. 复制 `docker-entrypoint.sh`
8. 默认启动命令：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

注意：

- 后端容器对外暴露的是 `8003`
- 当前 Docker 部署口径不是 README 中本地开发常见的 `8002`
- 处理部署问题时不要把本地运行端口和 Docker 运行端口混为一谈

### 6.2 docker/backend/docker-entrypoint.sh

后端容器启动时不是直接跑 `uvicorn`，而是先经过启动脚本，流程如下：

1. 等待 MySQL 可连接
2. 执行 `alembic upgrade head`
3. 如果 `KM_AUTO_INIT_DATA=true`，执行默认数据初始化
4. 启动 FastAPI 服务

这意味着当前部署链路自带以下设计：

- 数据库等待机制
- 自动迁移机制
- 可选的默认数据初始化机制

因此处理部署问题时要注意：

- 如果容器启动失败，不能只看 `uvicorn`，还要看是不是卡在数据库等待
- 如果数据库结构不一致，优先检查 entrypoint 的迁移阶段
- 如果线上出现“为什么默认账号被创建了”，要先检查 `.env.docker` 中的 `KM_AUTO_INIT_DATA`

## 七、前端镜像与 Nginx 代理细节

### 7.1 docker/frontend/Dockerfile

前端镜像构建流程：

1. 基于 `node:20-alpine` 构建前端
2. `COPY web/admin-frontend/package*.json`
3. 执行 `npm ci`
4. `COPY web/admin-frontend/ ./`
5. 执行 `npm run build`
6. 将 `dist` 拷贝到 Nginx 静态目录

这里有一个很重要的上下文：

- Docker 构建的是 `web/admin-frontend/` 这个真实前端工程
- 不是根目录另一个前端
- 也不是临时构造的静态页面

### 7.2 docker/frontend/nginx.conf

Nginx 当前承担两类职责：

1. 提供前端 SPA 静态资源
2. 反向代理后端接口与文档

当前代理规则：

- `/api/` → `http://backend:8003`
- `/docs` → `http://backend:8003`
- `/redoc` → `http://backend:8003`
- `/` → `try_files ... /index.html`

这意味着：

- 前端容器外部访问端口是 `5174`
- 前端刷新页面不会因为 history 路由直接 404
- 从浏览器访问前端后，可通过同域路径调用 `/api`

如果后续处理前端联调或 Nginx 代理问题，不要误以为前端直接请求宿主机 `localhost:8003`，当前 Docker 方案明确是通过 Nginx 反代 `backend` 容器名完成的。

## 八、代理设计与适用场景

### 8.1 为什么同时使用 `build.network: host` 和 `host.docker.internal`

设计目的：

1. 某些 Linux 服务器在镜像构建阶段访问宿主机代理不稳定
2. 单独配置 `host.docker.internal` 不一定足够
3. `build.network: host` 可以让构建阶段直接复用宿主机网络
4. `extra_hosts` 仍然保留一个可读、统一的宿主机别名

因此当前方案不是多余配置，而是为了兼容服务器实际网络环境做的稳定性设计。

### 8.2 代理作用范围

代理配置会影响：

- 后端镜像构建阶段 `pip install`
- 前端镜像构建阶段 `npm ci`
- 后端运行阶段访问外部网站

代理配置**不会**额外注入到前端 Nginx 运行阶段，因为它只负责静态资源和内网反代。

## 九、手工 Docker 部署标准流程

### 9.1 准备环境文件

先准备：

- `.env.docker`
- 应用业务环境文件，例如 `.env.production`

关键思路：

- `.env.docker` 管部署
- `.env.production` 管应用
- 用 `KM_APP_ENV_FILE` 把两者串起来

如果是首次部署，推荐先复制模板再修改：

```bash
cp .env.docker.example .env.docker
```

常见示例：

```env
KM_APP_ENV_FILE=.env.production
```

至少确认以下敏感或关键配置已按目标环境修改：

- `SECRET_KEY`
- `MYSQL_ROOT_PASSWORD`
- `DB_PASSWORD`
- `MYSQL_PASSWORD`
- `KM_APP_ENV_FILE`
- `KM_AUTO_INIT_DATA`

### 9.2 构建并启动

标准命令：

```bash
docker compose --env-file .env.docker build --no-cache
docker compose --env-file .env.docker up -d
```

说明：

- 使用 `--env-file .env.docker` 是为了让 Compose 在解析阶段就拿到 `KM_APP_ENV_FILE`
- `build --no-cache` 更适合部署、代理调试、依赖调整后的强制重建场景

如果只是首次部署且确认配置已经就绪，也可以直接使用一条命令：

```bash
docker compose --env-file .env.docker up -d --build
```

### 9.3 查看状态

```bash
docker compose --env-file .env.docker ps
docker compose --env-file .env.docker logs -f backend
docker compose --env-file .env.docker logs -f frontend
docker compose --env-file .env.docker logs -f mysql
```

### 9.4 默认数据初始化

默认情况下，部署不会自动创建管理员和测试账号。

如果只是测试环境，且希望首次启动时自动创建默认应用和默认账号，可以在 `.env.docker` 中设置：

```env
KM_AUTO_INIT_DATA=true
```

然后再执行：

```bash
docker compose --env-file .env.docker up -d --build
```

当前自动初始化会创建：

- 默认应用：`default_app`
- 管理员账号：`admin / admin123456`
- 测试账号：`testuser / test123456`

生产环境通常不建议开启。

如果未开启 `KM_AUTO_INIT_DATA=true`，首次部署后可手动初始化：

```bash
docker compose --env-file .env.docker exec backend python -m app.scripts.init_data 管理员账号 管理员密码
```

示例：

```bash
docker compose --env-file .env.docker exec backend python -m app.scripts.init_data admin MyStrongPassword123
```

如果只想单独创建管理员账号，也可以使用：

```bash
docker compose --env-file .env.docker exec backend python app/scripts/create_admin_user.py 管理员账号 管理员密码
```

### 9.5 访问地址

- 前端管理后台：`http://服务器IP:5174/`
- 后端 API：`http://服务器IP:8003/api/v1`
- Swagger：`http://服务器IP:8003/docs`
- ReDoc：`http://服务器IP:8003/redoc`

## 十、GitHub Actions 自动发布流程

当前自动发布工作流文件：

- `.github/workflows/deploy.yml`

触发条件：

- push 到 `master`
- 手动 `workflow_dispatch`

### 10.1 工作流的真实步骤

工作流通过 `appleboy/ssh-action` 登录 Linux 服务器，然后执行：

1. 关闭 BuildKit
2. 进入服务器项目目录
3. `git fetch --all --prune`
4. `git checkout master`
5. `git reset --hard origin/master`
6. `docker compose --env-file .env.docker build --no-cache`
7. `docker compose --env-file .env.docker up -d`
8. `docker compose --env-file .env.docker exec -T backend alembic upgrade head`
9. `docker image prune -f`
10. 输出当前容器状态

### 10.2 为什么工作流里用了 `git reset --hard`

这里的 `reset --hard` 不是普通开发场景建议，而是**部署目录显式设计**：

- 服务器项目目录被视为可重建产物
- 自动部署要求服务器代码与远程 `master` 完全一致
- 不保留服务器上的临时人工改动

因此后续如果 LLM 遇到“为什么部署脚本用了 reset --hard”，不要按本地开发安全规范去误判它，而要理解这是部署目录的强一致策略。

### 10.3 为什么工作流里关闭 BuildKit

工作流显式设置：

```bash
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
```

原因是当前服务器环境下，BuildKit 在 `docker compose build` 的镜像导出阶段存在兼容性或稳定性问题。

所以：

- 后续如果优化部署流程，不能想当然把 BuildKit 打开
- 必须先确认服务器环境已经解决该兼容问题，再考虑恢复

### 10.4 为什么工作流里迁移跑了两次

当前链路中：

- `backend` 容器启动时，`docker-entrypoint.sh` 已经会执行一次 `alembic upgrade head`
- 工作流完成 `up -d` 后，又显式执行一次：

```bash
docker compose --env-file .env.docker exec -T backend alembic upgrade head
```

这样设计的目的更偏稳妥性：

- 保证容器起来后数据库一定对齐到最新迁移
- 即使某次启动时迁移阶段出现边界情况，也再补一层显式执行

后续如果想优化这个流程，可以讨论是否保留双重迁移，但在没有充分验证前，不要轻易删掉其中一层。

## 十一、运维与排查建议

### 11.1 最小安全检查清单

部署到生产环境前，至少确认：

- 已修改 `SECRET_KEY`
- 已关闭 `DEBUG`
- 已设置强密码的数据库账号与管理员账号
- 已确认是否需要暴露 `8003`，或是否只通过前端 `5174` / 反向代理暴露服务
- 已确认日志目录、磁盘空间、数据库持久化卷策略

### 11.2 常用排查命令

```bash
docker compose --env-file .env.docker ps
docker compose --env-file .env.docker logs -f backend
docker compose --env-file .env.docker logs -f frontend
docker compose --env-file .env.docker logs -f mysql
docker compose --env-file .env.docker exec backend alembic current
docker compose --env-file .env.docker exec backend python app/scripts/verify_system.py
```

### 11.3 处理部署问题时的判断顺序

如果后续遇到 Docker 或自动发布问题，建议按下面顺序排查：

1. 先确认问题发生在：
   - 构建阶段
   - 容器启动阶段
   - 数据库迁移阶段
   - 前端 Nginx 代理阶段
   - GitHub Actions SSH 发布阶段
2. 再确认对应真实文件：
   - `docker-compose.yml`
   - 对应 Dockerfile
   - `docker-entrypoint.sh`
   - `nginx.conf`
   - `.github/workflows/deploy.yml`
3. 不要一上来就把问题归因到：
   - FastAPI 代码本身
   - Vue 页面本身
   - Docker 网络抽象概念
4. 优先判断是不是：
   - 代理配置错误
   - 环境文件没生效
   - 数据库未就绪
   - BuildKit 兼容问题
   - Nginx 代理路径不匹配
   - 服务器工作区和远程分支不一致

## 十二、文档治理说明

当前仓库的部署说明统一收口到本文档。

后续如果 Docker 编排、镜像构建、Nginx 代理、自动发布工作流发生变化，应优先同步更新：

- `app/docs/Docker部署与自动发布说明.md`
- `docker-compose.yml`
- `docker/`
- `.github/workflows/deploy.yml`

不要再并行维护多份含义重叠、口径不同的部署主文档，以免 LLM 或开发者读取后产生冲突理解。
