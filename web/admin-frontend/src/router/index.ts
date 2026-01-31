import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'

/**
 * 基础路由集合（登录页、403、404等）
 * @description 从 basic.ts 模块导入
 */
import basicRoutes from './basic'

/**
 * 业务路由集合（管理后台和通用页面）
 * @description 从 admin.ts 和 common.ts 模块导入
 */
import commonRoutes from './common'

/**
 * 动态导入所有路由模块
 * 使用 Vite 的 glob 导入功能，自动发现 modules 目录下的所有路由文件
 */
const modules = import.meta.glob("./modules/**/*.ts", { eager: true });

/**
 * 构建路由配置
 * 遍历所有动态导入的模块，提取路由配置
 */
const allRoutes: any[] = [];

console.log("routes: 所有的modules---", modules);
// 处理所有模块
Object.values(modules).forEach((module) => {
  console.log("routes: module---", module);
  // 获取模块的 default 导出
  const routeConfig = (module as any).default;

  console.log("routes: routeConfig---", routeConfig);

  if (routeConfig) {
    if (Array.isArray(routeConfig)) {
      // 如果是数组，使用 spread operator 添加
      allRoutes.push(...routeConfig);
    } else if (typeof routeConfig === "object") {
      // 如果是对象，直接添加
      allRoutes.push(routeConfig);
    }
  }
});

/**
 * 根据 meta.sort 排序路由
 * sort 值越小越靠前，没有 sort 的默认排在最后
 */
allRoutes.sort((a, b) => {
  const sortA = a.meta?.sort ?? Infinity;
  const sortB = b.meta?.sort ?? Infinity;
  return sortA - sortB;
});

/**
 * 构建路由配置
 * @description 将所有路由模块整合为完整的路由配置
 */
export const routes: RouteRecordRaw[] = [
  ...basicRoutes,
  // 主应用布局（需要认证）
  {
    path: '/',
    component: AdminLayout,
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      ...allRoutes,
      ...commonRoutes
    ]
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
