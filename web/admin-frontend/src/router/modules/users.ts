// 仪表盘路由配置
import { type RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  // 用户管理（仅管理员）
  {
    path: 'users',
    name: 'Users',
    component: () => import('@/views/user/index.vue'),
    meta: {
      title: '用户管理',
      icon: 'User',
      roles: ['admin'],
      sort: 2,
    }
  },
];

export default routes;