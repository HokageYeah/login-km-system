import { createApp } from 'vue'
import router from './router'
import pinia from './stores'
import '@/styles/index.css'
import 'element-plus/theme-chalk/el-message.css' // 引入 ElMessage 样式
import '@/router/permission' // 引入全局路由守卫
import { permission } from '@/directives/permission'

import App from './App.vue'

const app = createApp(App)

// 注册全局指令
app.directive('permission', permission)

app.use(pinia)
app.use(router)

app.mount('#app')
