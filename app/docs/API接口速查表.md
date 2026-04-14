# API 接口速查表

快速查找 API 接口的路径、方法和权限要求。

---

## 🔐 认证接口（无需登录）

| 方法 | 路径 | 说明 | 请求体 |
|------|------|------|--------|
| POST | `/api/v1/auth/register` | 用户注册 | `{username, password}` |
| POST | `/api/v1/auth/login` | 用户登录 | `{username, password, app_key, device_id}` |

---

## 👤 用户接口（需要登录）

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/v1/auth/verify` | 验证Token | 🔒 登录 |
| GET | `/api/v1/auth/me` | 获取当前用户信息 | 🔒 登录 |
| POST | `/api/v1/auth/logout` | 用户登出 | 🔒 登录 |

---

## 🎫 卡密管理接口（需要登录）

| 方法 | 路径 | 说明 | 请求体 | 权限 |
|------|------|------|--------|------|
| GET | `/api/v1/card/my` | 查询我的卡密 | - | 🔒 登录 |
| POST | `/api/v1/card/bind` | 绑定卡密 | `{card_key, device_id, device_name?}` | 🔒 登录 |
| POST | `/api/v1/card/unbind-device` | 解绑设备 | `{card_id, device_id}` | 🔒 登录 |
| GET | `/api/v1/card/{card_id}` | 查询卡密详情 | - | 🔒 登录 |

---

## 🏢 应用管理接口（需要管理员）

| 方法 | 路径 | 说明 | 请求体 | 权限 |
|------|------|------|--------|------|
| GET | `/api/v1/app/list` | 查询应用列表 | - | 🔑 管理员 |
| POST | `/api/v1/app/create` | 创建应用 | `{app_name, app_key?}` | 🔑 管理员 |
| POST | `/api/v1/app/{app_id}/status` | 更新应用状态 | `{status}` | 🔑 管理员 |
| GET | `/api/v1/app/{app_id}` | 查询应用详情 | - | 🔑 管理员 |

补充说明：

- `GET /api/v1/app/list` 现在除了应用基础字段，还会返回 `card_count`、`permission_count`
- 管理后台可以直接用这两个统计值做应用维度导航，无需逐行追加统计请求

---

## 🔑 权限校验接口

| 方法 | 路径 | 说明 | 请求体 | 权限 |
|------|------|------|--------|------|
| POST | `/api/v1/permission/check` | 权限校验 | `{permission, device_id?, card_id?}` | 🔒 登录 |
| POST | `/api/v1/permission/batch-check` | 批量权限校验 | `{permissions, device_id?, card_id?}` | 🔒 登录 |
| GET | `/api/v1/permission/my-permissions` | 查询我的权限 | `device_id?`, `card_id?` | 🔒 登录 |

---

## 👨‍💼 管理后台接口（开发中）

### 卡密管理
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/v1/admin/card/generate` | 批量生成卡密 | 🔑 管理员 |
| GET | `/api/v1/admin/cards` | 查询所有卡密（支持 `username` 筛选，并返回关联用户名） | 🔑 管理员 |
| POST | `/api/v1/admin/card/{card_id}/status` | 修改卡密状态 | 🔑 管理员 |
| POST | `/api/v1/admin/card/{card_id}/expire-time` | 修改卡密过期时间（按时间动态判断是否过期） | 🔑 管理员 |
| POST | `/api/v1/admin/card/{card_id}/permissions` | 修改卡密权限 | 🔑 管理员 |

### 用户管理
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/v1/admin/users` | 查询所有用户 | 🔑 管理员 |
| GET | `/api/v1/admin/user/{user_id}/active-cards` | 查询用户当前有效卡密详情 | 🔑 管理员 |
| PUT | `/api/v1/admin/user/{user_id}/status` | 封禁/解封用户 | 🔑 管理员 |

### 设备管理
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/v1/admin/devices` | 查询设备列表（支持 `card_key`、`username`，兼容 `card_id`、`user_id`） | 🔑 管理员 |
| PUT | `/api/v1/admin/device/{device_id}/status` | 禁用/启用设备 | 🔑 管理员 |

### 功能权限管理
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/v1/admin/feature-permissions/list` | 查询功能权限列表 | 🔑 管理员 |
| GET | `/api/v1/admin/feature-permissions/categories` | 查询功能权限分类 | 🔑 管理员 |
| POST | `/api/v1/admin/feature-permissions/export` | 导出当前勾选权限的快照文件 | 🔑 管理员 |
| POST | `/api/v1/admin/feature-permissions/import` | 导入权限快照文件并按 `permission_key` 写入数据库 | 🔑 管理员 |
| POST | `/api/v1/admin/feature-permissions/create` | 创建功能权限 | 🔑 管理员 |
| POST | `/api/v1/admin/feature-permissions/update/{permission_id}` | 更新功能权限 | 🔑 管理员 |
| POST | `/api/v1/admin/feature-permissions/delete/{permission_id}` | 删除功能权限 | 🔑 管理员 |
| POST | `/api/v1/admin/feature-permissions/batch-delete` | 批量删除功能权限，请求体为 `number[]` | 🔑 管理员 |

补充说明：

- 功能权限的“分类”在后台主视图中统一按“所属应用”理解；
- 导出会按应用分组携带权限，导入会按应用解析，不存在的应用会自动创建；
- 批量删除只删除权限元数据，不自动清理历史卡密中的旧 `permission_key`。

---

## 📖 图例说明

- 🔒 **登录**: 需要提供有效的 JWT Token
- 🔑 **管理员**: 需要管理员角色的 Token
- ✅ **已完成**: 接口已实现可用
- 🚧 **开发中**: 接口正在开发
- ⏳ **待开发**: 接口还未开始开发

---

## 🎯 快速测试

### 获取 Token
```bash
# 普通用户
curl -X POST "http://localhost:8003/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123456","app_key":"default_app","device_id":"test-001"}'

# 管理员
curl -X POST "http://localhost:8003/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123456","app_key":"default_app","device_id":"admin-001"}'
```

### 使用 Token
在后续请求中添加 Header：
```
Authorization: Bearer YOUR_TOKEN_HERE
```

---

## 📱 Swagger UI

访问交互式 API 文档：
```
http://localhost:8003/docs
```

在 Swagger UI 中：
1. 先调用登录接口获取 token
2. 点击右上角 🔒 "Authorize" 按钮
3. 输入 token
4. 就可以测试所有需要认证的接口了

---

## 🔍 接口状态

### 已完成接口（✅）
- 认证接口：5个
- 卡密管理接口：4个
- 应用管理接口：4个
- 权限校验接口：3个

**共计：16个接口**

### 待开发接口（⏳）
- 管理后台接口：约10个

---

**最后更新**: 2026-04-14
