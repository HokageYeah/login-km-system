import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

/**
 * 菜单项接口
 * @description 定义菜单的数据结构，用于SideMenu组件渲染
 */
export interface MenuItem {
  path: string
  name: string
  title: string
  icon?: string
  children?: MenuItem[]
}

/**
 * 生成菜单数据
 * @description 根据路由配置和用户角色动态生成菜单结构
 * @param routes 路由配置数组
 * @returns 符合当前用户权限的菜单列表
 */
export function generateMenus(routes: RouteRecordRaw[]): MenuItem[] {
  const userStore = useUserStore()
  const menus: MenuItem[] = []
  
  routes.forEach((route) => {
    // 只处理有title的路由（需要在菜单中显示的路由）
    if (route.meta && route.meta.title) {
      const roles = route.meta.roles as string[] | undefined
      
      // 如果没有roles限制，或者用户角色在允许的roles中，则显示该菜单
      if (!roles || roles.includes(userStore.role)) {
        const menuItem: MenuItem = {
          path: route.path,                    // 路由路径
          name: route.name as string,          // 路由名称
          title: route.meta.title as string,   // 菜单标题
          icon: route.meta.icon as string,     // 菜单图标
        }
        
        // 递归处理子菜单
        if (route.children && route.children.length > 0) {
           const subMenus = generateMenus(route.children)
           if (subMenus.length > 0) {
             menuItem.children = subMenus
           }
        }
        
        menus.push(menuItem)
      }
    }
  })
  
  return menus
}
