import type { RouteRecordRaw } from 'vue-router'

/**
 * 基础路由配置
 * @description 登录页、403、404等基础页面路由
 */
const routes: RouteRecordRaw[] = [
  // 登录页（无需认证）
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: {
      title: '登录',
      hidden: true // 不在菜单中显示
    }
  },
  // 403无权限页面
  {
    path: '/forbidden',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: { title: '无权限', hidden: true }
  },
  // 404页面（匹配所有未定义的路由）
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '404', hidden: true }
  }
]

export default routes
