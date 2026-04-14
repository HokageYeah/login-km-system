FROM python:3.11-slim

# 下面这组 ARG 是“可选构建参数”。
# 设计目标：
# 1. Linux 服务器需要代理时，可以通过 docker compose build.args 显式传入；
# 2. 本地开发如果没有配置这些值，就会自动使用默认空字符串；
# 3. 这样既兼容服务器代理环境，也不会破坏你本地已经验证通过的无代理构建流程。
ARG KM_DOCKER_HTTP_PROXY=""
ARG KM_DOCKER_HTTPS_PROXY=""
ARG KM_DOCKER_ALL_PROXY=""
ARG KM_DOCKER_NO_PROXY=""

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
# 这里把可选构建参数转成 Dockerfile 构建阶段可识别的标准代理变量。
# 如果对应 ARG 为空，下面这些 ENV 也只是空值，不会强制开启代理。
ENV HTTP_PROXY=${KM_DOCKER_HTTP_PROXY}
ENV HTTPS_PROXY=${KM_DOCKER_HTTPS_PROXY}
ENV ALL_PROXY=${KM_DOCKER_ALL_PROXY}
ENV NO_PROXY=${KM_DOCKER_NO_PROXY}
ENV http_proxy=${KM_DOCKER_HTTP_PROXY}
ENV https_proxy=${KM_DOCKER_HTTPS_PROXY}
ENV all_proxy=${KM_DOCKER_ALL_PROXY}
ENV no_proxy=${KM_DOCKER_NO_PROXY}

WORKDIR /app

COPY requirements.txt ./
# 这里通过标准代理环境变量向 pip 传递代理。
# 只有 Linux 服务器的 .env.docker 显式填写了 KM_DOCKER_* 参数时，pip install 才会走代理。
# 其他开发者或本地环境如果没有这些配置，构建行为与之前保持一致。
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY docker/backend/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8003

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
