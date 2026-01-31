// 仪表盘路由配置
import { type RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  // 卡密管理（仅管理员）
  {
    path: 'cards',
    name: 'Cards',
    component: () => import('@/views/card/index.vue'),
    meta: {
      title: '卡密管理',
      icon: 'Ticket',
      roles: ['admin'],
    }
  },
];

export default routes;