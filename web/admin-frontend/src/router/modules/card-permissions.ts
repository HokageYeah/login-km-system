// 仪表盘路由配置
import { type RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  // 功能权限管理（仅管理员）
  {
    path: 'card-permissions',
    name: 'CardPermissions',
    component: () => import('@/views/card-permission/index.vue'),
    meta: {
      title: '功能权限管理',
      icon: 'Lock',
      roles: ['admin'],
    }
  },
];

export default routes;