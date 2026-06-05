# 管理后台前端工程说明

这是“通用卡密与授权系统”的管理后台前端工程，不是默认 Vite 模板示例页，也不是独立于后端协议之外的演示项目。

当前前端的核心职责是：

- 为管理员提供用户、卡密、设备、应用、功能权限的管理界面
- 为管理员与普通用户提供统计数据、个人中心等通用页面
- 通过统一请求层对接后端 `/api/v1` 接口
- 在前端完成展示、路由与交互，不承担最终授权裁决

## 开发前必读

开始前建议至少阅读以下文档：

1. 项目全局规则：
   [.agent/rules/km-specs.md](/Users/yuye/YeahWork/Python项目/login-km-system/.agent/rules/km-specs.md)
2. 前端设计说明：
   [web/docs/管理后台前端设计说明（Vue3+TypeScript）.md](/Users/yuye/YeahWork/Python项目/login-km-system/web/docs/管理后台前端设计说明（Vue3+TypeScript）.md)
3. 前端布局说明：
   [web/docs/管理后台整体布局与交互设计说明.md](/Users/yuye/YeahWork/Python项目/login-km-system/web/docs/管理后台整体布局与交互设计说明.md)
4. 前端任务文档：
   [web/docs/管理后台前端设计任务.md](/Users/yuye/YeahWork/Python项目/login-km-system/web/docs/管理后台前端设计任务.md)
5. 路由专项文档：
   [docs/路由配置指南.md](/Users/yuye/YeahWork/Python项目/login-km-system/web/admin-frontend/docs/路由配置指南.md)
   [docs/路由系统升级说明.md](/Users/yuye/YeahWork/Python项目/login-km-system/web/admin-frontend/docs/路由系统升级说明.md)
6. 后端接口文档：
   [app/docs/API接口速查表.md](/Users/yuye/YeahWork/Python项目/login-km-system/app/docs/API接口速查表.md)

## 技术栈

- Vue 3
- TypeScript
- Vite
- Element Plus
- Pinia
- Vue Router
- Axios
- ECharts

## 当前真实目录结构

```text
web/admin-frontend/
├── docs/                    # 路由与前端专项说明
├── src/
│   ├── api/                 # 接口封装
│   ├── components/          # 通用组件
│   ├── directives/          # 自定义指令（如权限指令）
│   ├── layouts/             # 后台布局骨架
│   ├── router/              # 基础路由、业务路由、权限路由
│   ├── stores/              # Pinia 状态管理
│   ├── styles/              # 全局样式
│   ├── types/               # TypeScript 类型定义
│   ├── utils/               # 请求封装、菜单、价格、设备指纹等工具
│   └── views/               # 页面模块
├── package.json
└── vite.config.ts
```

## 主要页面模块

- `src/views/login/`：登录页
- `src/views/dashboard/`：仪表盘
- `src/views/user/`：用户管理
- `src/views/card/`：卡密管理
- `src/views/card-permission/`：功能权限管理
- `src/views/app/`：应用管理
- `src/views/device/`：设备管理
- `src/views/stats/`：统计数据
- `src/views/profile/`：个人中心
- `src/views/error/`：403 / 404 页面

## 路由与权限现状

- 路由入口：`src/router/index.ts`
- 基础路由：`src/router/basic.ts`
- 通用路由：`src/router/common.ts`
- 业务模块路由：`src/router/modules/*.ts`
- 布局容器：`src/layouts/AdminLayout.vue`
- 二级路由包装器：`src/layouts/components/RouterWrapper.vue`

当前路由机制要点：

- 登录、403、404 属于基础路由
- 业务页面挂载在 `AdminLayout` 下
- 一级路由与二级路由并存
- 有子路由的页面通过 `RouterWrapper` 提供 `<router-view>`
- 菜单展示依赖 `meta.title`、`meta.roles`、`meta.hidden`

## 开发约束

- 不要在页面组件里散落裸 `axios` 请求，优先走 `src/api/` 与 `src/utils/request.ts`
- 不要把后端授权判定复制到前端本地写死，前端只负责展示和请求发起
- 不要绕开现有 `router + stores + api + views + layouts` 结构平行再造一套新体系
- 涉及接口字段、状态语义、权限展示时，先核对后端文档和后端实现
- 尽量补充中文注释，尤其是类型、复杂交互、状态同步、路由权限逻辑

## 启动方式

### 安装依赖

```bash
npm install
```

### 本地开发

```bash
npm run dev
```

### 生产构建

```bash
npm run build
```

### 本地预览构建产物

```bash
npm run preview
```

## 环境变量

主要环境变量文件：

- `.env.development`
- `.env.production`

重点变量：

- `VITE_API_BASE_URL`：后端 API 基础地址
- `VITE_APP_TITLE`：前端页面标题

## 联调建议

- 先确认后端服务已启动，并且 `/api/v1` 接口可访问
- 先核对 `src/types/` 与后端响应字段是否一致
- 先核对 `src/api/` 与后端接口路径、参数、返回结构是否一致
- 如果某个页面出现展示异常，优先检查接口契约，而不是先在页面里加临时兼容分支
