# 部署指南

## 🚀 生产环境部署

### 环境要求

- Python 3.9+
- MySQL 5.7+ 或 8.0+
- 4GB+ 内存
- 20GB+ 磁盘空间

### 部署步骤

#### 1. 克隆代码

```bash
git clone <repository>
cd login-km-system
```

#### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置生产环境

编辑 `.env.production` 文件：

```bash
# 数据库配置
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=login_km_system_prod

# 安全配置
SECRET_KEY=your_very_secure_secret_key_here_min_32_chars
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 环境配置
ENVIRONMENT=production
DEBUG=False
```

#### 5. 创建数据库

```bash
# 设置环境为生产环境
export ENV=prod

# 创建数据库
python -m app.scripts.create_database
```

#### 6. 应用数据库迁移

```bash
python -m app.scripts.set_env prod upgrade
```

#### 7. 创建管理员账号

```bash
python app/scripts/create_admin_user.py admin your_secure_admin_password
```

#### 8. 启动服务

**方式一：直接启动**

```bash
python run_app.py
```

**方式二：使用Gunicorn（推荐）**

```bash
# 安装gunicorn
pip install gunicorn

# 启动（4个worker）
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:9999
```

**方式三：使用systemd（推荐）**

创建 `/etc/systemd/system/login-km-system.service`:

```ini
[Unit]
Description=Login KM System
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/login-km-system
Environment="ENV=prod"
ExecStart=/path/to/login-km-system/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:9999
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable login-km-system
sudo systemctl start login-km-system
sudo systemctl status login-km-system
```

#### 9. 配置Nginx反向代理

创建 `/etc/nginx/sites-available/login-km-system`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:9999;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/login-km-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 10. 配置HTTPS（推荐）

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 🐳 Docker部署

### 1. 创建Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 9999

# 启动命令
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:9999"]
```

### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "9999:9999"
    environment:
      - ENV=prod
      - DB_HOST=db
      - DB_USER=root
      - DB_PASSWORD=your_password
      - DB_NAME=login_km_system_prod
    depends_on:
      - db
    restart: always

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=your_password
      - MYSQL_DATABASE=login_km_system_prod
    volumes:
      - mysql_data:/var/lib/mysql
    restart: always

volumes:
  mysql_data:
```

### 3. 启动

```bash
docker-compose up -d
```

---

## 🔒 安全检查清单

部署前请确保：

- [ ] 修改了 SECRET_KEY 为强随机密钥
- [ ] 修改了管理员密码
- [ ] 数据库使用了独立账号（非root）
- [ ] 数据库密码足够强
- [ ] 配置了HTTPS
- [ ] 关闭了DEBUG模式
- [ ] 配置了防火墙
- [ ] 设置了日志轮转
- [ ] 配置了数据库备份

---

## 📊 监控和维护

### 日志查看

```bash
# 查看应用日志
tail -f logs/app_$(date +%Y-%m-%d).log

# 查看错误日志
grep ERROR logs/app_*.log
```

### 数据库备份

```bash
# 每天备份
0 2 * * * /usr/bin/mysqldump -u user -p'password' login_km_system_prod > /backup/db_$(date +\%Y\%m\%d).sql
```

### 性能监控

建议使用：
- Prometheus + Grafana
- 或者云服务商的监控工具

### 健康检查

```bash
# 检查服务状态
curl http://localhost:9999/

# 检查API文档
curl http://localhost:9999/docs

# 检查数据库连接
python app/scripts/verify_system.py
```

---

## 🆘 故障排查

### 服务无法启动

1. 检查端口是否被占用
   ```bash
   lsof -i:9999
   ```

2. 检查数据库连接
   ```bash
   mysql -u user -p -h host
   ```

3. 查看日志
   ```bash
   tail -100 logs/app_*.log
   ```

### 接口报错

1. 查看详细错误日志
2. 检查数据库数据是否正确
3. 验证Token是否有效
4. 检查权限配置

### 性能问题

1. 检查数据库索引
2. 查看慢查询日志
3. 增加缓存时间
4. 增加worker数量

---

## 📞 技术支持

- **文档**: app/docs/
- **API文档**: http://your-domain.com/docs
- **测试**: pytest tests/ -v
- **验证**: python app/scripts/verify_system.py

---

**部署完成后，建议进行完整的功能测试！**
