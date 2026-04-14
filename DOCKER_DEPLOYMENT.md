# Docker 部署说明

本项目已在根目录补齐 Docker Compose 部署文件，面向当前卡密系统的真实架构做了三层拆分：

- `mysql`：存储卡密、用户、设备、权限等核心业务数据
- `backend`：FastAPI 后端，负责所有授权裁决、后台管理与 API 输出
- `frontend`：Vue 管理后台，使用 Nginx 提供静态资源并反向代理 `/api`

## 目录说明

- `docker-compose.yml`：统一编排前端、后端、数据库
- `.env.docker`：Docker 部署专用环境变量
- `docker/backend/Dockerfile`：后端镜像构建文件
- `docker/backend/docker-entrypoint.sh`：后端启动入口，负责等待数据库、执行迁移、按需初始化数据
- `docker/frontend/Dockerfile`：前端镜像构建文件
- `docker/frontend/nginx.conf`：前端静态站和 API 代理配置

## 部署步骤

1. 先修改根目录 `.env.docker`

至少需要修改下面几项：

- `SECRET_KEY`
- `MYSQL_ROOT_PASSWORD`
- `DB_PASSWORD`
- `MYSQL_PASSWORD`

当前部署文件已经按现有项目端口约定配置完成：

- 后端对外暴露 `8003`
- 前端对外暴露 `5174`

2. 在项目根目录执行

```bash
docker compose up -d --build
```

3. 查看运行状态

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

## 访问地址

- 管理后台：`http://服务器IP:5174/`
- 后端 API：`http://服务器IP:8003/api/v1`
- Swagger 文档：`http://服务器IP:8003/docs`

## 默认数据初始化

默认情况下，部署不会自动创建管理员和测试账号。

如果你只是测试环境，想在首次启动时自动生成默认应用和默认账号，可以先把 `.env.docker` 里的 `KM_AUTO_INIT_DATA` 改为 `true`，再执行：

```bash
docker compose up -d --build
```

当前初始化脚本会创建：

- 默认应用：`default_app`
- 管理员账号：`admin / admin123456`
- 测试账号：`testuser / test123456`

生产环境不建议开启这个选项。更稳妥的做法是首次部署完成后，按你的账号策略手动初始化或通过后台创建。

## 说明

- 后端容器启动时会自动执行 `alembic upgrade head`，保证数据库结构与当前代码一致。
- 前端使用 `createWebHistory` 路由模式，所以 Nginx 已配置 `try_files`，直接刷新页面不会 404。
- 当前部署方案没有把授权判断下放到前端，仍然保持“服务端为最终授权裁决中心”的项目主设计不变。
