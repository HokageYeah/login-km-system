# 管理后台前端设计说明（Vue3 + TypeScript）

> 本文档用于指导 **通用卡密与授权系统** 的 **管理后台前端实现**。
>
> 技术栈：
>
> * Vue 3
> * TypeScript
> * Element Plus
> * Tailwind CSS
> * Vite
>
> 目标：
>
> * 提供一套 **清晰、可维护、可扩展** 的前端架构
> * 支持 **管理员 / 普通用户** 不同权限视图
> * 覆盖《系统使用手册》中提到的管理后台功能

---

## 一、整体定位与角色划分

### 1️⃣ 系统定位

该前端项目是：

> **通用卡密与授权平台的 Web 管理后台**

用于：

* 管理应用
* 管理用户
* 管理卡密
* 查看统计数据

---

### 2️⃣ 角色划分

| 角色         | 说明    | 可见页面       |
| ---------- | ----- | ---------- |
| 管理员（admin） | 系统运营者 | 所有功能模块     |
| 普通用户（user） | 被授权用户 | 仅“获取统计数据表” |

角色由后端返回，例如：

```json
{
  "role": "admin"
}
```

---

## 二、技术栈与基础约定

### 1️⃣ 技术选型

* **Vue 3**：Composition API
* **TypeScript**：强类型
* **Element Plus**：表单 / 表格 / 弹窗
* **Tailwind CSS**：布局 / 间距 / 视觉规范
* **Vue Router**：路由权限控制
* **Pinia**：全局状态管理
* **Axios**：HTTP 请求

---

### 2️⃣ 目录结构建议

```text
src/
├─ api/                # 接口封装
├─ assets/
├─ components/         # 全局通用组件（按钮、表格、弹窗等）
├─ layouts/            # 页面布局
├─ router/             # 路由 + 权限控制
├─ stores/             # Pinia 状态
├─ views/              # 页面（按业务模块划分）
│   ├─ login/
│   │   ├─ components/ # 登录模块私有组件
│   │   └─ index.vue
│   ├─ dashboard/
│   │   ├─ components/ # 仪表盘模块组件
│   │   └─ index.vue
│   ├─ user/
│   │   ├─ components/ # 用户管理模块组件
│   │   └─ index.vue
│   ├─ card/
│   │   ├─ components/ # 卡密管理模块组件
│   │   └─ index.vue
│   ├─ app/
│   │   ├─ components/ # 应用管理模块组件
│   │   └─ index.vue
│   ├─ stats/
│   │   ├─ components/ # 统计数据模块组件
│   │   └─ index.vue
│   └─ forbidden/
│       ├─ components/ # 无权限提示相关组件
│       └─ index.vue
├─ utils/
└─ main.ts
```

---

## 三、登录与权限控制设计

### 1️⃣ 登录页面（Login）

**路径**：`/login`

**功能**：

* 用户名 + 密码登录
* 登录成功后获取 token + role

**UI 结构**：

* 居中卡片
* Element Plus `el-form`
* 登录按钮 loading 状态

---

### 2️⃣ 登录请求参数

```json
{
  "username": "testuser",
  "password": "password123",
  "app_key": "wx_crawler_app",
  "device_id": "abc123def456"
}
```

**参数说明**：
- `username`: 用户名
- `password`: 密码
- `app_key`: 应用唯一标识（可选，默认使用当前应用）
- `device_id`: 设备唯一标识

---

### 3️⃣ 登录返回数据约定

```json
{
  "token": "jwt_token",
  "user_status": "normal",
  "has_card": false,
  "username": "testuser",
  "role": "admin"
}
```

**字段说明**：
- `token`: JWT Token，后续API调用的身份验证凭证
- `user_status`: 用户状态（normal/banned）
- `has_card`: 是否已绑定卡密
- `username`: 用户名
- `role`: 用户角色（admin/user）

---

### 4️⃣ 全局状态（Pinia）

---

### 3️⃣ 全局状态（Pinia）

```ts
interface UserState {
  token: string
  role: 'admin' | 'user'
  username: string
}
```

* token 持久化到 localStorage
* 页面刷新自动恢复登录态

---

### 4️⃣ 全局状态（Pinia）

```ts
interface UserState {
  token: string
  role: 'admin' | 'user'
  username: string
  user_status: 'normal' | 'banned'
  has_card: boolean
}
```

* token 持久化到 localStorage
* 页面刷新自动恢复登录态

---

### 5️⃣ 路由权限控制

#### 路由 meta 设计

```ts
meta: {
  requiresAuth: true,
  roles: ['admin']
}
```

#### 路由守卫逻辑

1. 未登录 → 跳转 `/login`
2. 已登录但角色不匹配 → 跳转 `/forbidden`
3. 合法 → 放行

---

## 三、API 接口设计

### 1️⃣ 认证接口

#### 1.1 用户注册

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}

Response:
{
  "id": 1,
  "username": "testuser",
  "status": "normal",
  "role": "user",
  "created_at": "2025-01-01T00:00:00"
}
```

#### 1.2 用户登录

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123",
  "app_key": "wx_crawler_app",
  "device_id": "abc123def456"
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user_status": "normal",
  "has_card": false,
  "username": "testuser",
  "role": "admin"
}
```

#### 1.3 Token 验证

```http
GET /api/v1/auth/verify
Authorization: Bearer {token}

Response:
{
  "user_id": 1,
  "username": "testuser",
  "status": "normal",
  "role": "admin",
  "app_id": 1,
  "device_id": "abc123def456"
}
```

#### 1.4 获取当前用户信息

```http
GET /api/v1/auth/me
Authorization: Bearer {token}

Response:
{
  "user_id": 1,
  "username": "testuser",
  "status": "normal",
  "role": "admin",
  "app_id": 1,
  "device_id": "abc123def456"
}
```

#### 1.5 用户登出

```http
POST /api/v1/auth/logout
Authorization: Bearer {token}

Response:
{
  "success": true,
  "message": "登出成功"
}
```

---

### 2️⃣ 应用管理接口（管理员）

#### 2.1 查询应用列表

```http
GET /api/v1/app/list
Authorization: Bearer {admin_token}

Response:
{
  "total": 2,
  "apps": [
    {
      "id": 1,
      "app_key": "wx_crawler_app",
      "app_name": "微信爬虫",
      "status": "normal",
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

#### 2.2 创建应用

```http
POST /api/v1/app/create
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "app_name": "新应用",
  "app_key": "new_app_key"
}

Response:
{
  "success": true,
  "message": "应用创建成功",
  "app": {
    "id": 2,
    "app_key": "new_app_a8f3e9",
    "app_name": "新应用",
    "status": "normal",
    "created_at": "2025-01-01T00:00:00"
  }
}
```

#### 2.3 更新应用状态

```http
POST /api/v1/app/{app_id}/status
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "disabled"
}

Response:
{
  "success": true,
  "message": "应用状态更新成功",
  "app": {
    "id": 1,
    "app_key": "wx_crawler_app",
    "app_name": "微信爬虫",
    "status": "disabled",
    "created_at": "2025-01-01T00:00:00"
  }
}
```

#### 2.4 查询应用详情

```http
GET /api/v1/app/{app_id}
Authorization: Bearer {admin_token}

Response:
{
  "id": 1,
  "app_key": "wx_crawler_app",
  "app_name": "微信爬虫",
  "status": "normal",
  "created_at": "2025-01-01T00:00:00"
}
```

---

### 3️⃣ 卡密管理接口

#### 3.1 查询我的卡密

```http
GET /api/v1/card/my
Authorization: Bearer {token}

Response:
{
  "has_card": true,
  "cards": [
    {
      "card_id": 1,
      "card_key": "ABCD-EFGH-IJKL-MNOP",
      "expire_time": "2026-01-01T00:00:00",
      "permissions": ["wechat", "ximalaya"],
      "bind_devices": 1,
      "max_device_count": 2,
      "status": "used",
      "remark": "高级套餐"
    }
  ]
}
```

#### 3.2 绑定卡密

```http
POST /api/v1/card/bind
Authorization: Bearer {token}
Content-Type: application/json

{
  "card_key": "ABCD-EFGH-IJKL-MNOP",
  "device_id": "abc123def456",
  "device_name": "MyPC"
}

Response:
{
  "success": true,
  "message": "卡密绑定成功",
  "card_info": {
    "card_id": 1,
    "card_key": "ABCD-EFGH-IJKL-MNOP",
    "expire_time": "2026-01-01T00:00:00",
    "permissions": ["wechat", "ximalaya"],
    "bind_devices": 1,
    "max_device_count": 2,
    "status": "used",
    "remark": "高级套餐"
  }
}
```

#### 3.3 解绑设备

```http
POST /api/v1/card/unbind-device
Authorization: Bearer {token}
Content-Type: application/json

{
  "card_id": 1,
  "device_id": "abc123def456"
}

Response:
{
  "success": true,
  "message": "设备解绑成功"
}
```

#### 3.4 查询卡密详情

```http
GET /api/v1/card/{card_id}
Authorization: Bearer {token}

Response:
{
  "card_id": 1,
  "card_key": "ABCD-EFGH-IJKL-MNOP",
  "app_name": "微信爬虫",
  "status": "used",
  "expire_time": "2026-01-01T00:00:00",
  "max_device_count": 2,
  "permissions": ["wechat", "ximalaya"],
  "remark": "高级套餐",
  "devices": [
    {
      "device_id": "abc123def456",
      "device_name": "MyPC",
      "bind_time": "2025-01-01T00:00:00",
      "last_active_at": "2025-01-01T12:00:00",
      "status": "active"
    }
  ],
  "created_at": "2025-01-01T00:00:00"
}
```

---

### 4️⃣ 管理后台接口（管理员）

#### 4.1 生成卡密

```http
POST /api/v1/admin/card/generate
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "app_id": 1,
  "count": 100,
  "expire_time": "2026-01-01T00:00:00",
  "max_device_count": 2,
  "permissions": ["wechat", "ximalaya"],
  "remark": "高级套餐"
}

Response:
{
  "success": true,
  "message": "成功生成 100 个卡密",
  "count": 100,
  "cards": [
    "ABCD-EFGH-IJKL-MNOP",
    "QRST-UVWX-YZ23-4567"
  ]
}
```

#### 4.2 查询用户列表

```http
GET /api/v1/admin/users?page=1&size=20&status=normal&keyword=test
Authorization: Bearer {admin_token}

Response:
{
  "total": 100,
  "page": 1,
  "size": 20,
  "users": [
    {
      "id": 1,
      "username": "testuser",
      "status": "normal",
      "role": "user",
      "created_at": "2025-01-01T00:00:00",
      "last_login_at": "2025-01-01T12:00:00"
    }
  ]
}
```

#### 4.3 更新用户状态

```http
POST /api/v1/admin/user/{user_id}/status?status=banned
Authorization: Bearer {admin_token}

Response:
{
  "success": true,
  "message": "用户状态更新成功: banned"
}
```

#### 4.4 查询卡密列表

```http
GET /api/v1/admin/cards?page=1&size=20&app_id=1&status=unused&keyword=ABCD
Authorization: Bearer {admin_token}

Response:
{
  "total": 100,
  "page": 1,
  "size": 20,
  "cards": [
    {
      "id": 1,
      "card_key": "ABCD-EFGH-IJKL-MNOP",
      "app_name": "微信爬虫",
      "status": "unused",
      "expire_time": "2026-01-01T00:00:00",
      "max_device_count": 2,
      "permissions": ["wechat"],
      "bind_count": 0,
      "remark": "高级套餐",
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

#### 4.5 更新卡密状态

```http
POST /api/v1/admin/card/{card_id}/status
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "disabled"
}

Response:
{
  "success": true,
  "message": "卡密状态更新成功: disabled"
}
```

#### 4.6 更新卡密权限

```http
POST /api/v1/admin/card/{card_id}/permissions
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "permissions": ["wechat"]
}

Response:
{
  "success": true,
  "message": "卡密权限更新成功"
}
```

#### 4.7 查询设备列表

```http
GET /api/v1/admin/devices?page=1&size=20&card_id=1&user_id=1&status=active
Authorization: Bearer {admin_token}

Response:
{
  "total": 50,
  "page": 1,
  "size": 20,
  "devices": [
    {
      "id": 1,
      "card_id": 1,
      "card_key": "ABCD-EFGH-IJKL-MNOP",
      "user_id": 1,
      "username": "testuser",
      "device_id": "abc123def456",
      "device_name": "MyPC",
      "bind_time": "2025-01-01T00:00:00",
      "last_active_at": "2025-01-01T12:00:00",
      "status": "active"
    }
  ]
}
```

#### 4.8 更新设备状态

```http
POST /api/v1/admin/device/{device_id}/status
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "disabled"
}

Response:
{
  "success": true,
  "message": "设备状态更新成功: disabled"
}
```

#### 4.9 获取统计数据

```http
GET /api/v1/admin/statistics
Authorization: Bearer {admin_token}

Response:
{
  "total_users": 100,
  "total_cards": 1000,
  "unused_cards": 500,
  "used_cards": 500,
  "disabled_cards": 0,
  "total_devices": 200,
  "active_devices": 180,
  "total_apps": 2,
  "normal_apps": 2,
  "today_new_users": 10,
  "today_new_cards": 50
}
```

---

### 5️⃣ 权限校验接口

#### 5.1 权限校验

```http
POST /api/v1/permission/check
Authorization: Bearer {token}
Content-Type: application/json

{
  "permission": "wechat",
  "device_id": "abc123def456"
}

Response:
{
  "allowed": true,
  "message": "权限验证通过",
  "expire_time": "2026-01-01T00:00:00"
}

或

{
  "allowed": false,
  "message": "卡密已过期",
  "expire_time": null
}
```

---

## 四、整体布局设计（Layout）

---

## 四、整体布局设计（Layout）

### 1️⃣ 布局结构

```text
┌───────────────┐
│ TopBar        │  用户名 / 退出
├───────┬───────┤
│ Side  │ Main  │
│ Menu  │ View  │
└───────┴───────┘
```

* 管理员：显示完整菜单
* 普通用户：只显示【统计数据】

---

### 2️⃣ 菜单权限控制

菜单数据由前端根据 role 生成：

```ts
const adminMenus = [
  '应用管理',
  '用户管理',
  '卡密管理',
  '统计数据'
]

const userMenus = [
  '统计数据'
]
```

---

## 五、功能模块页面设计（管理员）

### 1️⃣ 仪表盘（Dashboard）

**路径**：`/dashboard`

**接口调用**：`GET /api/v1/admin/statistics`

**功能**：

* 用户总数、今日新增
* 卡密总数、未使用/已使用/禁用
* 设备总数、活跃设备
* 应用总数、正常应用

**实现建议**：

* Element Plus `el-card`
* Tailwind Grid 布局
* 显示统计数据卡片

---

### 2️⃣ 应用管理（App Management）

**路径**：`/app`

**接口列表**：
* `GET /api/v1/app/list` - 查询应用列表
* `POST /api/v1/app/create` - 创建应用
* `POST /api/v1/app/{app_id}/status` - 更新应用状态
* `GET /api/v1/app/{app_id}` - 查询应用详情

功能：

* 应用列表（表格展示）
* 新增应用（弹窗）
* 启用/禁用应用

页面结构：

* 表格（应用名称、app_key、状态、创建时间、操作）
* 新增按钮
* 新增/编辑弹窗

**新增应用表单字段**：

* 应用名称
* app_key（可选，不填自动生成）

---

### 3️⃣ 用户管理（User Management）

**路径**：`/user`

**接口列表**：
* `GET /api/v1/admin/users?page={page}&size={size}&status={status}&keyword={keyword}` - 查询用户列表
* `POST /api/v1/admin/user/{user_id}/status?status={status}` - 更新用户状态

功能：

* 用户列表（分页、状态筛选、关键词搜索）
* 封禁/解封用户

重点：

* 状态列高亮（normal-绿色、banned-红色）
* 操作二次确认

**用户列表表格字段**：

* ID
* 用户名
* 角色
* 状态
* 创建时间
* 最后登录时间
* 操作（封禁/解封）

---

### 4️⃣ 卡密管理（Card Management）

**路径**：`/card`

**接口列表**：
* `GET /api/v1/admin/cards?page={page}&size={size}&app_id={app_id}&status={status}&keyword={keyword}` - 查询卡密列表
* `POST /api/v1/admin/card/generate` - 生成卡密
* `POST /api/v1/admin/card/{card_id}/status` - 更新卡密状态
* `POST /api/v1/admin/card/{card_id}/permissions` - 更新卡密权限
* `GET /api/v1/admin/devices?card_id={card_id}` - 查询设备列表

功能：

* 卡密列表（分页、应用筛选、状态筛选、搜索）
* 生成卡密
* 禁用/启用卡密
* 修改权限
* 查看绑定设备

#### 卡密列表表格字段

* ID
* 卡密
* 应用名称
* 状态（unused/used/disabled）
* 过期时间
* 最大设备数
* 已绑定设备数
* 权限
* 备注
* 创建时间
* 操作（禁用/启用、修改权限、查看设备）

#### 卡密生成弹窗

字段：

* 应用（下拉选择）
* 数量（数字输入）
* 过期时间（日期时间选择器）
* 最大设备数（数字输入）
* 权限（多选框）
* 备注（文本输入）

#### 修改权限弹窗

字段：

* 权限（多选框，动态添加选项）

#### 设备列表弹窗

表格字段：

* 设备ID
* 设备名称
* 用户名
* 绑定时间
* 最后活跃时间
* 状态
* 操作（禁用/启用）

---

### 5️⃣ 统计数据（Stats）【管理员 & 普通用户】

**路径**：`/stats`

**接口调用**：`GET /api/v1/admin/statistics`

功能：

* 与仪表盘相同的统计数据展示
* 数据可视化（图表，可选）
* 导出数据（可选）

**数据展示**：

* 用户统计：总数、今日新增、活跃用户
* 卡密统计：总数、未使用、已使用、禁用、今日生成
* 设备统计：总数、活跃设备、今日新增
* 应用统计：总数、正常应用

普通用户登录后：

> **只显示该页面，其余菜单不可见**

---

## 六、公共组件设计

### 1️⃣ 权限指令（可选）

```ts
v-permission="'admin'"
```

用于按钮级权限控制。

---

### 2️⃣ 通用表格组件

封装：

* loading
* 分页
* 搜索栏

---

## 七、接口与异常处理

### 1️⃣ Axios 封装

* 自动携带 token
* 401 → 跳登录
* 403 → 跳 forbidden

---

### 2️⃣ Forbidden 页面

**路径**：`/forbidden`

提示：

> “当前账号无权限访问该页面”

---

## 八、UI 与样式约定

* Element Plus 负责功能组件
* Tailwind 负责：

  * 布局
  * 间距
  * 响应式

风格目标：

> **干净、偏工具型、不过度花哨**

---

## 九、开发顺序建议

1. 登录页 + Token 管理
2. Layout + 路由权限
3. 统计数据页（用户 / 管理员共用）
4. 卡密管理
5. 用户管理
6. 应用管理

---

## 十、设计原则总结

* 权限控制 **前后端双重校验**
* 菜单 ≠ 权限（仅做 UI 引导）
* 所有核心规则由后端决定

---

> 本前端设计目标：
> **让你以后加新功能，只需要加页面，不需要重构权限体系。**

---

## 十三、TypeScript 类型定义

### 1️⃣ 用户相关类型

```ts
// 用户状态
export type UserRole = 'admin' | 'user'
export type UserStatus = 'normal' | 'banned'

// 用户信息
export interface User {
  id: number
  username: string
  status: UserStatus
  role: UserRole
  created_at: string
  last_login_at?: string
}

// 用户列表响应
export interface UserListResponse {
  total: number
  page: number
  size: number
  users: User[]
}
```

### 2️⃣ 应用相关类型

```ts
// 应用状态
export type AppStatus = 'normal' | 'disabled'

// 应用信息
export interface App {
  id: number
  app_key: string
  app_name: string
  status: AppStatus
  created_at: string
}

// 应用列表响应
export interface AppListResponse {
  total: number
  apps: App[]
}
```

### 3️⃣ 卡密相关类型

```ts
// 卡密状态
export type CardStatus = 'unused' | 'used' | 'disabled'

// 卡密信息
export interface Card {
  id: number
  card_id: number
  card_key: string
  app_id?: number
  app_name?: string
  status: CardStatus
  expire_time: string
  max_device_count: number
  permissions: string[]
  bind_count?: number
  bind_devices?: number
  remark?: string
  created_at: string
}

// 卡密列表响应
export interface CardListResponse {
  total: number
  page: number
  size: number
  cards: Card[]
}

// 设备信息
export interface Device {
  id: number
  card_id: number
  card_key: string
  user_id?: number
  username?: string
  device_id: string
  device_name?: string
  bind_time: string
  last_active_at: string
  status: 'active' | 'disabled'
}

// 设备列表响应
export interface DeviceListResponse {
  total: number
  page: number
  size: number
  devices: Device[]
}
```

### 4️⃣ 统计相关类型

```ts
// 统计数据
export interface Statistics {
  total_users: number
  total_cards: number
  unused_cards: number
  used_cards: number
  disabled_cards: number
  total_devices: number
  active_devices: number
  total_apps: number
  normal_apps: number
  today_new_users: number
  today_new_cards: number
}
```

### 5️⃣ API 请求类型

```ts
// 登录请求
export interface LoginRequest {
  username: string
  password: string
  app_key?: string
  device_id?: string
}

// 登录响应
export interface LoginResponse {
  token: string
  user_status: UserStatus
  has_card: boolean
  username: string
  role: UserRole
}

// 创建应用请求
export interface CreateAppRequest {
  app_name: string
  app_key?: string
}

// 生成卡密请求
export interface GenerateCardRequest {
  app_id: number
  count: number
  expire_time: string
  max_device_count: number
  permissions: string[]
  remark?: string
}

// 通用响应
export interface CommonResponse {
  success: boolean
  message: string
}
```

---

## 十四、环境配置

### 1️⃣ 环境变量

```env
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api/v1

# .env.production
VITE_API_BASE_URL=https://api.example.com/api/v1
```

### 2️⃣ API 基础配置

```ts
// src/api/config.ts
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})
```

---

## 十五、注意事项

### 1️⃣ 安全性

* Token 必须存储在 localStorage 中
* 敏感操作需要二次确认
* 不要在前端显示完整卡密（除管理员查看）
* 登出时清除 Token

### 2️⃣ 性能优化

* 使用分页加载数据
* 避免频繁的 API 调用
* 合理使用缓存
* 组件懒加载

### 3️⃣ 用户体验

* 加载状态提示
* 错误信息友好提示
* 操作成功反馈
* 表单验证提示

### 4️⃣ 代码规范

* 使用 TypeScript 类型
* 组件命名规范
* 文件命名规范
* 注释清晰
* 代码格式化（Prettier）

---

## 十六、测试建议

### 1️⃣ 单元测试

* 组件测试
* 工具函数测试
* Store 测试

### 2️⃣ 集成测试

* 页面功能测试
* API 调用测试
* 路由测试

### 3️⃣ E2E 测试

* 完整流程测试
* 用户场景测试

---

> 本文档作为管理后台前端开发的指导文档，涵盖了从项目初始化到部署的完整流程。
