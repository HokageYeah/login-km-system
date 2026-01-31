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
 * 生成菜单数据（内部实现）
 * @description 根据路由配置和用户角色动态生成菜单结构
 * @param routes 路由配置数组
 * @param parentPath 父级路由路径（用于构建完整的菜单路径）
 * @returns 符合当前用户权限的菜单列表
 */
function generateMenusRecursive(
  routes: RouteRecordRaw[],
  parentPath: string = ''
): MenuItem[] {
  const userStore = useUserStore()
  const menus: MenuItem[] = []

  routes.forEach((route) => {
    // 只处理有meta的路由
    if (route.meta) {
      // 第一步：检查 hidden 属性，如果 hidden 为 true，则不在菜单中显示
      if (route.meta.hidden) {
        return
      }

      // 第二步：检查是否需要显示（有 title 才显示）
      if (!route.meta.title) {
        return
      }

      // 第三步：检查角色权限
      const roles = route.meta.roles as string[] | undefined
      // 如果有 roles 限制，则只有用户角色在其中时才显示
      // 如果没有 roles，则默认显示
      if (roles && !roles.includes(userStore.role)) {
        return
      }

      // 构建完整的路径
      // 如果 parentPath 为空（一级菜单），需要加上 '/' 前缀
      // 如果 parentPath 不为空（二级菜单），使用父路径拼接
      let fullPath: string
      if (!parentPath) {
        // 一级菜单：确保以 '/' 开头
        fullPath = route.path.startsWith('/') ? route.path : `/${route.path}`
      } else {
        // 二级菜单：拼接父路径
        fullPath = `${parentPath}/${route.path}`
      }

      // 创建菜单项
      const menuItem: MenuItem = {
        path: fullPath,                       // 完整路由路径
        name: route.name as string,          // 路由名称
        title: route.meta.title as string,   // 菜单标题
        icon: route.meta.icon as string,     // 菜单图标
      }

      // 递归处理子菜单
      if (route.children && route.children.length > 0) {
        const subMenus = generateMenusRecursive(route.children, fullPath)
        if (subMenus.length > 0) {
          menuItem.children = subMenus
        }
      }

      menus.push(menuItem)
    }
  })

  return menus
}

/**
 * 生成菜单数据（对外接口）
 * @description 从主应用布局的 children 中提取菜单数据，并根据用户角色动态生成
 * @param routes 完整的路由配置数组
 * @returns 符合当前用户权限的菜单列表
 */
export function generateMenus(routes: RouteRecordRaw[]): MenuItem[] {
  // 查找主应用布局（path 为 '/' 的路由）
  const mainAppRoute = routes.find(route => route.path === '/')

  if (!mainAppRoute || !mainAppRoute.children || mainAppRoute.children.length === 0) {
    console.warn('未找到主应用布局的子路由')
    return []
  }

  console.log('主应用布局 children:', mainAppRoute.children)

  // 从主应用布局的 children 中生成菜单
  return generateMenusRecursive(mainAppRoute.children, '')
}

