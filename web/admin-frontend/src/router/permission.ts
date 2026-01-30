import router from './index'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置 NProgress
NProgress.configure({ showSpinner: false })

/**
 * 全局路由守卫
 * @description 在每次路由跳转前进行权限验证
 */
router.beforeEach(async (to, from, next) => {
  // 开启进度条
  NProgress.start()
  
  const userStore = useUserStore()
  
  // 设置页面标题
  document.title = `${to.meta.title ? to.meta.title + ' - ' : ''}卡密管理系统`

  /**
   * 1. 白名单处理：登录页
   * 如果用户已登录，再次访问登录页则跳转到后台首页
   */
  if (to.path === '/login') {
    if (userStore.isLoggedIn) {
      next('/dashboard') // 已登录，跳转首页
    } else {
      next() // 未登录，允许访问
    }
    NProgress.done()
    return
  }

  /**
   * 2. 登录验证
   * 检查路由是否需要认证 (requiresAuth)
   */
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!userStore.isLoggedIn) {
      // 未登录，跳转登录页，并记录重定向地址
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      NProgress.done()
      return
    }

    /**
     * 3. 用户信息获取（可选）
     * 如果已登录但无用户信息（例如页面刷新），尝试重新获取
     */
    if (!userStore.username && userStore.token) {
       try {
         await userStore.fetchUserInfo()
       } catch (error) {
         // 获取失败（如Token失效），登出并重定向
         await userStore.logout()
         ElMessage.error('认证失效，请重新登录')
         next('/login')
         NProgress.done()
         return
       }
    }

    /**
     * 4. 角色权限验证
     * 检查用户角色是否有权限访问当前路由
     */
    const requiredRoles = to.meta.roles as string[] | undefined
    if (requiredRoles && requiredRoles.length > 0) {
      if (!requiredRoles.includes(userStore.role)) {
         next('/forbidden') // 无权限跳转
         NProgress.done()
         return
      }
    }
  }

  // 验证通过，放行
  next()
})

router.afterEach(() => {
  // 关闭进度条
  NProgress.done()
})
