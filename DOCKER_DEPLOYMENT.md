# Docker 部署说明

本项目已在根目录补齐 Docker Compose 部署文件，面向当前卡密系统的真实架构做了三层拆分：

- `mysql`：存储卡密、用户、设备、权限等核心业务数据
- `backend`：FastAPI 后端，负责所有授权裁决、后台管理与 API 输出
- `frontend`：Vue 管理后台，使用 Nginx 提供静态资源并反向代理 `/api`

## 目录说明

- `docker-compose.yml`：统一编排前端、后端、数据库
- `.env.docker`：Docker 部署专用环境变量
- `.env.production` / `.env.development` / `.env.test`：应用层环境文件，存放 `DB_*`、`SECRET_KEY`、`DEBUG` 等真实业务配置
- `docker/backend/Dockerfile`：后端镜像构建文件
- `docker/backend/docker-entrypoint.sh`：后端启动入口，负责等待数据库、执行迁移、按需初始化数据
- `docker/frontend/Dockerfile`：前端镜像构建文件
- `docker/frontend/nginx.conf`：前端静态站和 API 代理配置

## 部署步骤

1. 先准备 Docker 环境变量文件

推荐做法：

```bash
cp .env.docker.example .env.docker
```

然后再修改根目录 `.env.docker`

并确认 `KM_APP_ENV_FILE` 指向了你当前部署需要的应用环境文件，例如：

```env
KM_APP_ENV_FILE=.env.production
```

至少需要修改下面几项：

- `SECRET_KEY`
- `MYSQL_ROOT_PASSWORD`
- `DB_PASSWORD`
- `MYSQL_PASSWORD`

如果你的 Linux 服务器访问 Docker Hub、PyPI、npm 仓库必须经过代理，还需要按实际环境补下面这些可选项：

- `KM_DOCKER_HTTP_PROXY`
- `KM_DOCKER_HTTPS_PROXY`
- `KM_DOCKER_ALL_PROXY`
- `KM_DOCKER_NO_PROXY`

示例：

```env
KM_DOCKER_HTTP_PROXY=http://127.0.0.1:8118
KM_DOCKER_HTTPS_PROXY=http://127.0.0.1:8118
KM_DOCKER_ALL_PROXY=socks5://127.0.0.1:1080
KM_DOCKER_NO_PROXY=localhost,127.0.0.1,::1,mysql
```

设计说明：

- 这些代理配置只从 `.env.docker` 读取；
- 你本地如果不填写，就不会启用代理；
- 因此本地 Docker 测试会保持原来的无代理构建行为，不会被服务器代理设置污染。

更具体地说：

- `KM_DOCKER_HTTP_PROXY`：给 `pip install`、`npm ci` 和后端运行时 HTTP 请求使用
- `KM_DOCKER_HTTPS_PROXY`：给 HTTPS 请求使用
- `KM_DOCKER_ALL_PROXY`：给需要全局代理的场景使用，例如 `socks5://...`
- `KM_DOCKER_NO_PROXY`：给本地地址和内网服务做白名单，避免访问数据库、localhost 时错误绕到代理

如果你的服务器没有代理：

```env
KM_DOCKER_HTTP_PROXY=
KM_DOCKER_HTTPS_PROXY=
KM_DOCKER_ALL_PROXY=
KM_DOCKER_NO_PROXY=localhost,127.0.0.1,::1,mysql
```

如果你的服务器需要代理：

```env
KM_DOCKER_HTTP_PROXY=http://127.0.0.1:8118
KM_DOCKER_HTTPS_PROXY=http://127.0.0.1:8118
KM_DOCKER_ALL_PROXY=socks5://127.0.0.1:1080
KM_DOCKER_NO_PROXY=localhost,127.0.0.1,::1,mysql
```

注意：

- 这里的代理地址必须是“Docker 构建阶段和容器运行阶段能访问到的地址”；
- 如果你填写了 `127.0.0.1`，默认表示代理服务就运行在当前这台 Linux 服务器本机上；
- 如果其他同事的服务器没有部署代理服务，请不要照抄这一组值，直接留空即可。

当前部署文件已经按现有项目端口约定配置完成：

- 后端对外暴露 `8003`
- 前端对外暴露 `5174`

补充说明：

- `.env.docker` 负责“部署层配置”，例如代理、MySQL 初始化参数、Compose 选环境文件；
- `.env.production` / `.env.development` / `.env.test` 负责“应用层配置”，例如 `DB_*`、`SECRET_KEY`；
- 当前通过 `.env.docker` 中的 `KM_APP_ENV_FILE` 决定 backend 容器最终使用哪一套应用环境。

2. 在项目根目录执行

```bash
docker compose --env-file .env.docker up -d --build
```

如果你修改了代理配置，建议显式重建镜像，避免继续复用旧缓存：

```bash
docker compose --env-file .env.docker build --no-cache
docker compose --env-file .env.docker up -d
```

这里显式加 `--env-file .env.docker` 的原因是：

- Docker Compose 需要在启动前就解析 `KM_APP_ENV_FILE`；
- 加上这个参数后，Compose 会直接读取 `.env.docker` 中的 `KM_APP_ENV_FILE`；
- 从而把 `.env.production` / `.env.development` / `.env.test` 正确注入 backend 容器。

3. 查看运行状态

```bash
docker compose --env-file .env.docker ps
docker compose --env-file .env.docker logs -f backend
docker compose --env-file .env.docker logs -f frontend
```

## 访问地址

- 管理后台：`http://服务器IP:5174/`
- 后端 API：`http://服务器IP:8003/api/v1`
- Swagger 文档：`http://服务器IP:8003/docs`

## 默认数据初始化

默认情况下，部署不会自动创建管理员和测试账号。

如果你只是测试环境，想在首次启动时自动生成默认应用和默认账号，可以先把 `.env.docker` 里的 `KM_AUTO_INIT_DATA` 改为 `true`，再执行：

```bash
docker compose --env-file .env.docker up -d --build
```

当前初始化脚本会创建：

- 默认应用：`default_app`
- 管理员账号：`admin / admin123456`
- 测试账号：`testuser / test123456`

生产环境不建议开启这个选项。更稳妥的做法是首次部署完成后，按你的账号策略手动初始化或通过后台创建。

如果你没有设置 `KM_AUTO_INIT_DATA=true`，镜像启动后需要手动执行初始化命令。

推荐命令：

```bash
docker compose --env-file .env.docker exec backend python -m app.scripts.init_data 管理员账号 管理员密码
```

示例：

```bash
docker compose --env-file .env.docker exec backend python -m app.scripts.init_data admin MyStrongPassword123
```

说明：

- 这个命令会创建默认应用 `default_app`
- 同时创建你指定的管理员账号
- 还会补测试账号 `testuser`
- 如果管理员账号已存在，脚本会跳过重复创建

如果你只想单独创建管理员账号，也可以使用：

```bash
docker compose --env-file .env.docker exec backend python app/scripts/create_admin_user.py 管理员账号 管理员密码
```

## 说明

- 后端容器启动时会自动执行 `alembic upgrade head`，保证数据库结构与当前代码一致。
- 前端使用 `createWebHistory` 路由模式，所以 Nginx 已配置 `try_files`，直接刷新页面不会 404。
- 当前部署方案没有把授权判断下放到前端，仍然保持“服务端为最终授权裁决中心”的项目主设计不变。
- 代理配置同时作用于：
  - 后端镜像构建阶段的 `pip install`
  - 前端镜像构建阶段的 `npm ci`
  - 后端容器运行时访问外部网站的请求
- 前端运行容器本身没有额外注入代理，因为它最终只是 Nginx 提供静态文件，不承担外网业务请求。
