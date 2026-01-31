// 仪表盘路由配置
import { type RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  // 应用管理（仅管理员）
  {
    path: 'apps',
    name: 'Apps',
    component: () => import('@/views/app/index.vue'),
    meta: {
      title: '应用管理',
      icon: 'Grid',
      roles: ['admin'],
    }
  },
];

export default routes;