// 仪表盘路由配置
import { type RouteRecordRaw } from "vue-router";
import RouterWrapper from '@/layouts/components/RouterWrapper.vue';

const routes: Array<RouteRecordRaw> = [
    {
        path: 'dashboard',
        component: RouterWrapper,
        meta: {
          title: '仪表盘',
          icon: 'DataLine',
          roles: ['admin'],
          sort: 1,
        },
        children: [
          {
            path: 'table',
            name: 'Dashboard',
            component: () => import('@/views/dashboard/index.vue'),
            meta: {
              title: '表格数据',
              icon: 'DataLine',
              roles: ['admin'],
            }
          },
          {
            path: 'dashboard2',
            name: 'Dashboard2',
            component: () => import('@/views/dashboard/index2.vue'),
            meta: {
              title: '测试页面',
              icon: 'DataLine',
              roles: ['admin'],
            }
          }
        ]
      },
];

export default routes;