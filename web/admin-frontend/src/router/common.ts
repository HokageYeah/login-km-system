import type { RouteRecordRaw } from 'vue-router'

/**
 * 通用路由配置
 * @description 管理员和普通用户都可访问的页面路由
 */
const routes: RouteRecordRaw[] = [
  // 统计数据（管理员和普通用户都可访问）
  {
    path: 'stats',
    name: 'Stats',
    component: () => import('@/views/stats/index.vue'),
    meta: {
      title: '统计数据',
      icon: 'DataAnalysis',
      roles: ['admin', 'user'],
    }
  },
  // 个人中心（管理员和普通用户都可访问）
  {
    path: 'profile',
    name: 'Profile',
    component: () => import('@/views/profile/index.vue'),
    meta: {
      title: '个人中心',
      icon: 'User',
      roles: ['admin', 'user'],
      hidden: true, // 不在菜单中显示
    }
  }
]

export default routes
