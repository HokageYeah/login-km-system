#!/bin/sh
set -eu

echo "等待 MySQL 服务可用..."
python - <<'PY'
import os
import sys
import time

import mysql.connector

host = os.getenv("DB_HOST", "mysql")
port = int(os.getenv("DB_PORT", "3306"))
user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD", "")
database = os.getenv("DB_NAME")
max_attempts = int(os.getenv("DB_WAIT_MAX_ATTEMPTS", "60"))
sleep_seconds = float(os.getenv("DB_WAIT_INTERVAL", "2"))

for attempt in range(1, max_attempts + 1):
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connection_timeout=3,
        )
        connection.close()
        print(f"MySQL 已就绪，第 {attempt} 次尝试连接成功")
        break
    except Exception as exc:
        print(f"等待 MySQL 中（第 {attempt}/{max_attempts} 次）：{exc}")
        time.sleep(sleep_seconds)
else:
    print("MySQL 长时间未就绪，停止启动后端容器", file=sys.stderr)
    sys.exit(1)
PY

echo "执行 Alembic 数据库迁移..."
alembic upgrade head

if [ "${KM_AUTO_INIT_DATA:-false}" = "true" ]; then
  echo "检测到 KM_AUTO_INIT_DATA=true，开始初始化默认数据..."
  python -m app.scripts.init_data
else
  echo "跳过默认数据初始化"
fi

echo "启动 FastAPI 服务..."
exec "$@"
