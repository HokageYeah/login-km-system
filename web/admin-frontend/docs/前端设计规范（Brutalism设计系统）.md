# 管理后台前端设计规范（Brutalism / Creative Agency 设计系统）

> 本文档是 `web/admin-frontend/` 的**唯一视觉设计基准**。后续所有新页面、新组件、改版维护
> 都必须遵循本规范。风格参考：https://uupm.cc/demo/creative-agency （Creative Agency 演示页）。
>
> 设计系统的唯一代码实现位于 `src/styles/index.css`，本文档与其保持同步；
> 两者冲突时以代码为准并回头修正本文档。

---

## 1. 设计语言定位

**粗野主义（Brutalism）× Creative Agency**：高对比、平面色块、实体感交互。

核心特征（一眼识别）：

1. **奶油纸色底** + **近黑墨色**文字，对比度 WCAG AA 以上
2. **2px 实线黑边框**，**全直角**（radius = 0）
3. **硬阴影**（offset 实体阴影，如 `4px 4px 0 #141414`），不用弥散投影
4. **电光黄 `#FFC700`** 唯一强强调色；粉 `#FF90E8`、蓝 `#4D9DE0` 仅作低频点缀
5. **900 字重大标题** + 黄色荧光笔衬底 + 编号角标（01/02/03）
6. 交互"按压感"：hover 位移 `-2px,-2px` + 阴影放大，active 反向压回
7. 跑马灯（marquee）黑底黄字条，内容从最右侧进场、跑出左侧后循环

---

## 2. 设计令牌（CSS 变量）

定义在 `src/styles/index.css` 的 `:root`，**页面代码只允许引用令牌，禁止写死色值**。

### 2.1 色彩

| 令牌 | 值 | 用途 |
|---|---|---|
| `--ink` | `#141414` | 墨色：边框、标题、主按钮 hover 底、表头底 |
| `--ink-soft` | `#57534e` | 次级文字（暖灰，奶油底上对比度 ≥ 4.5:1） |
| `--paper` | `#f1ede2` | 页面背景（奶油纸色） |
| `--surface` | `#fffdf6` | 卡片 / 表格 / 面板表面（暖白） |
| `--line-soft` | `#dcd5c6` | 表格内部细线、次级分隔 |
| `--accent` | `#ffc700` | 电光黄：CTA、激活态、高亮、hover |
| `--accent-soft` | `#fff3bf` | 黄弱化版：hover 背景、行选中、日期区间 |
| `--accent-pink` | `#ff90e8` | 粉：低频点缀（应用图标块等） |
| `--accent-blue` | `#4d9de0` | 蓝：低频点缀（用户/设备图标块等） |
| `--danger` | `#e5484d` | 危险语义：删除、封禁、禁用 |
| 语义色 | success `#1a7f37` / warning `#b45309` | 仅通过边框与文字色表达 |

### 2.2 阴影（三档硬阴影）

| 令牌 | 值 | 用途 |
|---|---|---|
| `--shadow-brutal-sm` | `3px 3px 0 var(--ink)` | 按钮、输入框聚焦、小元素 |
| `--shadow-brutal` | `4px 4px 0 var(--ink)` | 卡片、面板、表格 |
| `--shadow-brutal-lg` | `8px 8px 0 var(--ink)` | 对话框、抽屉、大弹层 |

### 2.3 布局

| 令牌 | 值 | 用途 |
|---|---|---|
| `--topbar-height` | `92px` | 顶栏总高（跑马灯 28 + 导航 64），内容区高度计算统一引用 |

---

## 3. 布局规范

- **侧边栏**：260px 展开 / 64px 折叠，纸色底 + 2px 黑右边框；Logo 区黑底 + 黄色方块图标；
  菜单激活态 = 黄底黑字 + 2px 黑框 + `3px 3px 0` 硬阴影
- **顶栏**：`sticky` 吸顶，结构 = 黑底黄字跑马灯条(28px) + 暖白导航条(64px，2px 黑下边框)
- **内容区**：纸色底 `p-6`；各列表页容器 `p-8`；`min-height: calc(100vh - var(--topbar-height))`
- **关键约束**：`.main-container { min-width: 0 }` —— flex 子项必须置 0，
  否则宽表格会把整个页面撑出视口（历史 bug，勿删）
- **表格宽度策略**：所有表格 `width: 100%` 占满内容区；列总和超宽时由表格自身底部
  横向滚动条承接（已加高 10px + 墨色拇指），**页面永远不出横向滚动**

---

## 4. 组件规范

所有 Element Plus 组件外观已由全局主题接管（`src/styles/index.css`）。
**scoped 样式只写布局定位，不写组件皮肤**；新增组件优先复用以下形态。

### 4.1 按钮

| 形态 | 观感 | 用途 |
|---|---|---|
| 主按钮（primary） | **电光黄底 + 黑字 + 2px 黑框 + 硬阴影**，hover 反转黑底黄字 | 工具栏"创建/保存/确定"、登录 |
| 默认按钮（default） | 暖白底 + 黑框黑字 + 硬阴影，hover 黄底 | 刷新、取消、次要操作 |
| 危险按钮（danger） | 红底白字（实心）或红框红字（plain/link），hover 红底白字 | 删除、封禁、禁用 |
| 成功按钮（success） | 绿 `#1a7f37` 同上语义规则 | 启用、解封 |
| 表格迷你按钮 | 暖白底 + 2px 黑框 + `2px 2px 0` 微阴影 + 700 字重；语义色仅描边/文字 | 表格行内操作（`.el-table` 作用域自动生效） |

### 4.2 标签（el-tag → 硬边徽章）

暖白底 + 2px 语义色描边 + 语义色加粗文字 + 微型硬阴影，直角。五种语义色统一规则。

### 4.3 表格

- 外框 2px 黑；**黑表头（奶油色文字、800 字重）+ 表头下 3px 电光黄粗线**
- 行分隔 1px `--line-soft`；行 hover 黄弱化底
- 表格底部横向滚动条：10px 高、墨色方块拇指

### 4.4 对话框 / 抽屉

2px 黑框 + `8px 8px 0` 硬阴影 + 直角；**标题栏黑底** + 纸色 900 字重标题 + 黄色关闭按钮
（hover 黄底黑字）。弹窗内 Hero 区可用黑底块 + 黄色眉题 + 旋转几何色块装饰。

### 4.5 输入类（input / select / textarea / date-picker）

白底 + 2px 黑框直角；**聚焦 = 黑色描边 + `3px 3px 0` 黄色偏移阴影**。
日期面板：选中日黑底黄字、今日加粗下划线、区间黄弱化底。

### 4.6 其他

- 分页：方形按钮 + 黑框，当前页黑底黄字
- 分段控制器（segmented）：黑框 + 选中项黑底黄字
- 深色 tooltip：墨底黄字直角
- 面包屑：当前页黑体加粗
- 滚动条：墨色方块拇指
- 复选/单选：方形黑框，选中墨色实心

---

## 5. 排版规范

- **页面主标题**：`text-3xl`、`font-weight: 900`、`letter-spacing: -0.02em`、墨色 +
  黄色荧光笔衬底（标准写法：`background: linear-gradient(to top, var(--accent) 32%, transparent 32%); display: inline-block; padding: 0 0.15em;`）
- **面板标题**：`font-weight: 900` 墨色
- **次级文字**：`var(--ink-soft)` + `font-weight: 600` 及以上
- **数字**：一律 `font-variant-numeric: tabular-nums`（等宽，表格/统计不跳动）
- **字体栈**：系统字体（`Helvetica Neue / PingFang SC / Microsoft YaHei`），
  **禁止引入外部字体服务**（内网部署不依赖外网）
- **大写与字距**：拉丁眉题（kicker）用 `letter-spacing: 0.1em~0.2em` 加粗小字

---

## 6. 交互与动效规范

- 全局过渡 **150ms** `cubic-bezier(0.2, 0, 0, 1)`（粗野主义要"脆"，不要绵软的 300ms+）
- 悬停位移反馈：卡片 `-2px,-2px` + 阴影放大至 `6px 6px`；按钮 `-1px,-1px`
- 按压：`active` 位移 `+1px,+1px` + 阴影收平（"实体按压感"）
- **禁止** scale 缩放 hover（引起布局抖动）
- **禁止** 弥散阴影过渡、长时间位移动画
- 必须尊重 `prefers-reduced-motion`（全局已处理，新增动画自行遵守）
- 跑马灯：`padding-left: 100%` + `translateX(0 → -100%)` 单段循环，
  内容从容器最右进场、完全跑出左侧后再从右侧出现；悬停暂停

---

## 7. 新页面 / 新组件开发清单

1. 页面容器：`background: var(--paper)`，列表页 `p-8`，`min-height: calc(100vh - var(--topbar-height))`
2. 主标题套荧光笔衬底标准写法；面板用 `.brutal-card` 语言（surface + 2px 黑框 + 硬阴影）
3. 卡片 hover 套 `.brutal-hover`（位移 + 阴影放大）
4. EP 组件（按钮/表格/弹窗/输入框/标签/分页）**直接使用，不写皮肤覆盖**——全局主题已接管
5. 图标色块：平面色 + 2px 黑框直角，色相用令牌（用户=蓝、卡密=黄、设备=绿、应用=粉）
6. scoped 样式只写布局（flex/grid/间距/定位），色值与皮肤一律引用令牌
7. 中文注释解释"为什么"

---

## 8. 禁止清单（出现即需回改）

| 禁止 | 替代 |
|---|---|
| EP 默认蓝 / `bg-blue-*`、`text-blue-*` | 令牌色 |
| 圆角 `rounded-*`（卡片/按钮/输入框） | 直角 |
| 弥散阴影 `shadow-sm/md/lg` | 三档硬阴影令牌 |
| 渐变背景 / 渐变文字 / 毛玻璃 backdrop-filter | 平面色块 |
| scale 缩放 hover | 位移 + 阴影 |
| 写死 hex 色值 | 设计令牌 |
| 外部字体 @import | 系统字体栈 |
| EP 扁平 link/text 按钮（透明无边） | 全局已重定义，勿在页面再覆盖回扁平 |

---

## 9. 已知豁免（历史原因，不强制回改）

1. **ECharts 图表内部配色**：颜色常量写在各页面 `<script>` 中，属业务脚本域，
   保持冷色调未强改（如需统一需单独立项）
2. **应用标签颜色**：`src/utils/app-tag.ts` 内联驱动 8 组柔和粉彩，保留
   "同一应用跨页面同色"语义；直角与黑边仍由全局生效
3. `HomeView.vue` 为未挂路由的死代码，未改版

---

## 10. 关键文件位置

| 文件 | 职责 |
|---|---|
| `src/styles/index.css` | **设计系统唯一实现**：令牌 + EP 全局覆盖 + 通用工具类 |
| `src/layouts/AdminLayout.vue` | 布局骨架（含 `min-width: 0` 关键约束） |
| `src/layouts/components/SideMenu.vue` | 侧边栏（黑 Logo 块、黄激活态） |
| `src/layouts/components/TopBar.vue` | 顶栏（跑马灯条 + sticky 吸顶） |
| `src/views/login/index.vue` | 登录页（几何装饰 + 跑马灯 + 荧光笔标题范本） |
| `src/views/dashboard/index.vue` | 看板页（编号角标、黄/黑粗顶边面板范本） |
| `src/components/BaseCard.vue` / `BaseButton.vue` | 通用卡片/按钮组件 |

> ⚠️ **级联顺序约定**：`src/main.ts` 中必须 **先引入 `element-plus/dist/index.css`，
> 再引入 `@/styles/index.css`**。顺序颠倒会导致全局主题的同优先级直接规则被 EP 压掉，
> 页面退回"一半参考风格、一半 Element Plus 默认风格"（历史 bug，勿回退）。
