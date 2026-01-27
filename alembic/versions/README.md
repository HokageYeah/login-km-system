# 数据库迁移说明

## 迁移脚本列表

### 001_create_auth_system_tables.py
**创建时间**: 2026-01-27  
**描述**: 创建授权系统的6个核心表

包含的表：
1. **apps** - 应用表
2. **users** - 用户表
3. **cards** - 卡密表
4. **user_cards** - 用户-卡密绑定表
5. **card_devices** - 卡密-设备绑定表
6. **user_tokens** - 用户Token表

## 如何应用迁移

### 方法一：使用 alembic 命令（推荐）

```bash
# 1. 确保已安装依赖
pip install -r requirements.txt

# 2. 设置环境变量（选择开发/测试/生产环境）
export ENV=dev  # 或 test, prod

# 3. 应用迁移到最新版本
alembic upgrade head

# 4. 验证迁移是否成功
# 连接数据库查看表是否创建
```

### 方法二：使用项目脚本

```bash
# 应用迁移
python -m app.scripts.set_env dev upgrade

# 查看当前版本
python -m app.scripts.set_env dev current

# 回滚一个版本
python -m app.scripts.set_env dev downgrade
```

### 方法三：直接使用 Python

```python
from alembic import command
from alembic.config import Config

# 加载配置
alembic_cfg = Config("alembic.ini")

# 应用迁移
command.upgrade(alembic_cfg, "head")
```

## 验证迁移

应用迁移后，请验证以下内容：

1. **表是否创建成功**
   ```sql
   SHOW TABLES;
   ```

2. **表结构是否正确**
   ```sql
   DESC apps;
   DESC users;
   DESC cards;
   DESC user_cards;
   DESC card_devices;
   DESC user_tokens;
   ```

3. **索引是否创建**
   ```sql
   SHOW INDEX FROM cards;
   ```

4. **外键约束是否存在**
   ```sql
   SELECT 
       TABLE_NAME,
       COLUMN_NAME,
       CONSTRAINT_NAME,
       REFERENCED_TABLE_NAME,
       REFERENCED_COLUMN_NAME
   FROM
       INFORMATION_SCHEMA.KEY_COLUMN_USAGE
   WHERE
       REFERENCED_TABLE_NAME IS NOT NULL
       AND TABLE_SCHEMA = 'your_database_name';
   ```

## 回滚迁移

如果需要回滚到之前的版本：

```bash
# 回滚一个版本
alembic downgrade -1

# 回滚到初始状态
alembic downgrade base

# 回滚到指定版本
alembic downgrade 001
```

## 注意事项

1. **备份数据库**: 在执行迁移前，建议备份数据库
2. **测试环境验证**: 先在测试环境验证迁移脚本
3. **生产环境迁移**: 生产环境迁移需要谨慎，建议在低峰期执行
4. **权限检查**: 确保数据库用户有创建表、索引、外键的权限
5. **字符集**: 所有表使用 `utf8mb4` 字符集，支持 emoji 等特殊字符

## 常见问题

### 1. 迁移失败：表已存在
**解决方案**: 检查数据库中是否已经有同名表，如果有，需要先删除或重命名

### 2. 迁移失败：外键约束错误
**解决方案**: 检查被引用的表是否存在，外键约束的顺序是否正确

### 3. 如何查看迁移历史
```bash
alembic history
alembic current
```

### 4. 如何跳过某个迁移
```bash
# 标记为已执行，但不实际执行
alembic stamp 001
```
