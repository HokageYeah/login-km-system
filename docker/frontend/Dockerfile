FROM node:20-alpine AS builder

# 前端镜像也补上同一组可选代理参数。
# 原因不是前端运行时要走代理，而是服务器在镜像构建阶段执行 npm ci 时，
# 同样可能需要访问国外 npm 仓库。
# 如果未显式传值，这些参数全部为空，不会影响本地原有流程。
# 如果代理跑在 Linux 宿主机上，建议在 .env.docker 中把代理地址写成：
# http://host.docker.internal:端口
# 并配合 docker-compose.yml 中的 build.extra_hosts + build.network: host 使用。
ARG KM_DOCKER_HTTP_PROXY=""
ARG KM_DOCKER_HTTPS_PROXY=""
ARG KM_DOCKER_ALL_PROXY=""
ARG KM_DOCKER_NO_PROXY=""

# 这里同样把可选构建参数映射为标准代理环境变量。
# 保持和后端 Dockerfile 的语义一致，减少后续维护时的认知成本。
ENV HTTP_PROXY=${KM_DOCKER_HTTP_PROXY}
ENV HTTPS_PROXY=${KM_DOCKER_HTTPS_PROXY}
ENV ALL_PROXY=${KM_DOCKER_ALL_PROXY}
ENV NO_PROXY=${KM_DOCKER_NO_PROXY}
ENV http_proxy=${KM_DOCKER_HTTP_PROXY}
ENV https_proxy=${KM_DOCKER_HTTPS_PROXY}
ENV all_proxy=${KM_DOCKER_ALL_PROXY}
ENV no_proxy=${KM_DOCKER_NO_PROXY}
# 限制 Node.js 在前端构建阶段的最大堆内存。
# 设计说明：
# 1. 当前项目在 Linux 小内存云服务器上执行 `vue-tsc -b && vite build` 时，
#    有概率因为瞬时内存占用过高被系统 OOM Killer 直接杀掉；
# 2. 增加这一限制后，可以降低 Node 构建阶段的峰值内存使用，减少 exit code 137；
# 3. 这里不是为了“提速”，而是为了让自动部署在资源紧张的服务器上更稳定；
# 4. 1536MB 对当前项目通常足够，如果后续前端规模继续增长，再按实际构建日志调整。
ENV NODE_OPTIONS=--max-old-space-size=1536

WORKDIR /build

COPY web/admin-frontend/package*.json ./
# npm ci 是否走代理，完全取决于上面的 KM_DOCKER_* 参数是否有值。
# 因此本地不配置时，依然保持你原来的无代理构建行为。
# 如果 Linux 服务器代理部署在宿主机本机，推荐使用：
# KM_DOCKER_HTTP_PROXY=http://host.docker.internal:8118
# KM_DOCKER_HTTPS_PROXY=http://host.docker.internal:8118
# 同时 docker-compose.yml 中建议为 frontend.build 配置：
# - network: host
# - extra_hosts: ["host.docker.internal:host-gateway"]
RUN npm ci

COPY web/admin-frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine

COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /build/dist /usr/share/nginx/html

EXPOSE 5174

CMD ["nginx", "-g", "daemon off;"]
