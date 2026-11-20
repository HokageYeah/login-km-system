import { createApp } from 'vue'
import router from './router'
import pinia from './stores'
// 注意引入顺序：Element Plus 样式必须先于全局主题引入。
// 原因：styles/index.css 中大量组件覆盖是与 EP 同优先级的直接规则（如 2px 黑边框、
// 硬阴影、hover 位移），若 EP 样式在后加载，会把它们整体压掉，导致页面呈现
// "一半参考风格、一半 Element Plus 默认风格"。CSS 变量类覆盖不受顺序影响。
import 'element-plus/dist/index.css' // 引入完整的 Element Plus 样式
import '@/styles/index.css' // 全局设计系统（必须在 EP 之后）
import '@/router/permission' // 引入全局路由守卫
import { permission } from '@/directives/permission'

import App from './App.vue'

const app = createApp(App)

// 注册全局指令
app.directive('permission', permission)

app.use(pinia)
app.use(router)

app.mount('#app')
