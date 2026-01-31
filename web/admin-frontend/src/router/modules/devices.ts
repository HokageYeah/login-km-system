// 仪表盘路由配置
import { type RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  // 设备管理（仅管理员）
  {
    path: 'devices',
    name: 'Devices',
    component: () => import('@/views/device/index.vue'),
    meta: {
      title: '设备管理',
      icon: 'Monitor',
      roles: ['admin'],
    }
  },
];

export default routes;