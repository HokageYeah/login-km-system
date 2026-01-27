---
trigger: always_on
---

# Cursor 通用工程规则（Rules）- Vue 3 版

## 一、语言与输出约定

- 所有回复、说明、注释、文档 **必须使用简体中文**
- 代码中的标识符保持英文，不使用拼音
- 错误信息、日志内容允许为英文

## 二、技术默认约定

- 前端：默认使用 **Vue 3 (Composition API) + TypeScript**
- 后端：默认使用 **Python（优先 FastAPI）**
- 若无特殊说明，均遵循以上技术选型

## 三、通用代码规范

### 命名规范

- 变量 / 函数：camelCase
- 类 / 组件：PascalCase
- 常量：UPPER_SNAKE_CASE
- 文件 / 文件夹：kebab-case (例如：`user-profile.vue`, `use-auth.ts`)

命名应语义清晰，禁止随意缩写。

### 注释规范（强制）

- 注释用于解释「为什么这样设计」，而不是代码字面含义
- 复杂逻辑、业务判断、边界条件必须写注释
- 禁止无意义注释

统一注释标记：

```ts
// TODO: 待实现功能
// FIXME: 已知问题或潜在缺陷
// NOTE: 重要设计说明
// HACK: 临时方案，后续必须重构
```

#### 函数注释规范

前端（JSDoc）：

```ts
/**
 * 获取用户信息
 * @param userId 用户 ID
 * @returns 用户数据
 */
```

后端（Python Docstring）：

```python
def get_user(user_id: str):
    """
    根据用户 ID 获取用户信息
    """
```

## 四、前端规范（Vue 3）

### 基本原则

- 必须使用 **SFC (Single File Components)** 结构
- 必须使用 **`<script setup>`** 语法糖
- 使用 **Composition API**，禁止使用 Options API
- 单个组件只承担单一职责，逻辑复杂时通过 **Composables** (自定义 Hook) 抽离

### 命名约定

- 组件名使用 PascalCase (例如：`UserCard.vue`)
- 文件夹/文件名使用 kebab-case (例如：`components/user-card.vue`)
- 自定义 Composables 必须以 `use` 开头 (例如：`useUserData.ts`)

```vue
<!-- UserCard.vue -->
<template>
  <!-- 视图层 -->
</template>

<script setup lang="ts">
// 逻辑层
</script>
```

### 响应式规范

- 优先使用 `ref()` 定义响应式变量，以保持类型一致性
- 只有在处理深度嵌套的对象或明确需要对象整体响应时才使用 `reactive()`
- 解构 `props` 或 `reactive` 对象时必须使用 `toRefs` 以防丢失响应性

### Props & Emits 规范

- 必须使用 TypeScript 的 **类型定义声明**
- Props 推荐使用 `defineProps<Props>()` 方式
- 非必传参数使用 `?`
- 事件必须使用 `defineEmits` 声明

```ts
interface Props {
  user: User;
  active?: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: "update", id: number): void;
}>();
```

### 性能与结构要求

- 避免在 `v-for` 中同时使用 `v-if`（应使用 computed 过滤列表）
- `v-for` 必须绑定稳定的 `key`
- 大数据列表使用虚拟滚动 (Virtual Scroll)
- 合理使用 `shallowRef` 或 `markRaw` 处理不需要深层响应的大型数据对象
- 组件与路由采用异步导入/懒加载

## 五、后端规范（Python）

### 基本要求

- Python ≥ 3.10
- 优先使用 FastAPI
- 所有函数与方法必须标注类型
- 禁止使用裸 `except`
- 禁止使用 `print` 作为日志方式

### 分层结构（必须遵守）

- api：请求解析与响应封装
- service：业务逻辑处理
- repository：数据库访问
- schema：请求 / 响应数据校验
- model：ORM 模型定义

禁止在 api 层直接操作数据库。

### 日志规范

- 使用 logging 模块
- 合理区分日志级别（DEBUG / INFO / WARNING / ERROR）
- 日志中不得包含敏感信息

## 六、安全规范（重点）

### 通用安全原则

- 永远不信任客户端输入
- 所有输入必须进行校验
- 敏感操作必须经过身份与权限校验

### 前端安全

- 禁止使用 `v-html` 渲染不受信任的内容（防止 XSS）
- 敏感数据（如 Token）不存储在 localStorage，推荐使用 HttpOnly Cookie 或 Vuex/Pinia 内存存储
- 提交表单需防范 CSRF 攻击

### 后端安全

- 使用 Pydantic 进行参数校验
- 权限校验必须在 service 层完成
- 所有密钥从环境变量中读取

```python
import os
SECRET_KEY = os.getenv("SECRET_KEY")
```

- 敏感字段返回前需脱敏
- 密码等敏感数据必须加密存储

## 七、AI 协作使用规范

- 所有自动生成的代码必须遵守本规则
- 生成结果应：
  - 结构清晰（Vue 3 `<script setup>` + TS）
  - 类型完整
  - 逻辑解构合理（Composable 化）
  - 安全可靠
- 不生成不必要的复杂实现，保持 Vue 简洁的响应式特性控制。
