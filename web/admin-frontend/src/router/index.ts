import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'

/**
 * 路由配置
 * @description 定义系统所有路由，包括页面路径、权限要求等
 */
export const routes: RouteRecordRaw[] = [
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
  // 主应用布局（需要认证）
  {
    path: '/',
    component: AdminLayout,
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      // 仪表盘（仅管理员）
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { 
          title: '仪表盘',                     // 菜单标题
          icon: 'DataLine',                    // 菜单图标
          roles: ['admin'],                     // 允许访问的角色
          hidden: true                         // 不在菜单中显示
        }
      },
      // 用户管理（仅管理员）
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/user/index.vue'),
        meta: { 
          title: '用户管理', 
          icon: 'User', 
          roles: ['admin'],
          hidden: true                         // 不在菜单中显示
        }
      },
      // 卡密管理（仅管理员）
      {
        path: 'cards',
        name: 'Cards',
        component: () => import('@/views/card/index.vue'),
        meta: { 
          title: '卡密管理', 
          icon: 'Ticket', 
          roles: ['admin'],
          hidden: true                         // 不在菜单中显示
        }
      },
      // 设备管理（仅管理员）
      {
        path: 'devices',
        name: 'Devices',
        component: () => import('@/views/device/index.vue'),
        meta: { 
          title: '设备管理', 
          icon: 'Monitor', 
          roles: ['admin'],
          hidden: true                         // 不在菜单中显示
        }
      },
      // 应用管理（仅管理员）
      {
        path: 'apps',
        name: 'Apps',
        component: () => import('@/views/app/index.vue'),
        meta: {
          title: '应用管理',
          icon: 'Grid',
          roles: ['admin'],
          hidden: true                         // 不在菜单中显示
        }
      },
      // 功能权限管理（仅管理员）
      {
        path: 'card-permissions',
        name: 'CardPermissions',
        component: () => import('@/views/card-permission/index.vue'),
        meta: {
          title: '功能权限管理',
          icon: 'Lock',
          roles: ['admin'],
          hidden: true                         // 不在菜单中显示
        }
      },
      // 统计数据（管理员和普通用户都可访问）
      {
        path: 'stats',
        name: 'Stats',
        component: () => import('@/views/stats/index.vue'),
        meta: { 
          title: '统计数据', 
          icon: 'DataAnalysis', 
          roles: ['admin', 'user'],
          hidden: true                         // 不在菜单中显示
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
          hidden: true                         // 不在菜单中显示
        }
      }
    ]
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

/**
 * 创建路由实例
 * @description 使用HTML5 History模式
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
