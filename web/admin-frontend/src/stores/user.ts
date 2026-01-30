import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getCurrentUser, logout as apiLogout } from '@/api/auth'
import type { LoginRequest, UserRole, UserStatus } from '@/types'

/**
 * 用户状态接口
 * @description 定义用户在Pinia Store中的状态结构
 */
interface UserState {
  token: string                 // JWT Token
  username: string              // 用户名
  role: UserRole | ''           // 用户角色（admin/user），初始为空
  user_status: UserStatus | ''  // 用户状态（normal/banned），初始为空
  has_card: boolean             // 是否已绑定卡密
}

/**
 * 用户状态管理 Store
 * @description 管理用户登录状态、个人信息及权限角色。使用 Setup Store 模式。
 */
export const useUserStore = defineStore('user', () => {
  // ==================== State (状态) ====================
  
  const token = ref<string>('')
  const username = ref<string>('')
  const role = ref<UserRole | ''>('')
  const userStatus = ref<UserStatus | ''>('')
  const hasCard = ref<boolean>(false)

  // ==================== Getters (计算属性) ====================
  
  /**
   * 是否已登录
   * @description 通过判断是否存在Token来确定登录状态
   */
  const isLoggedIn = computed(() => !!token.value)

  /**
   * 是否为管理员
   * @description 判断当前用户角色是否为 admin
   */
  const isAdmin = computed(() => role.value === 'admin')

  // ==================== Actions (操作方法) ====================

  /**
   * 设置 Token
   * @param t 新的 Token 字符串
   */
  function setToken(t: string) {
    token.value = t
  }

  /**
   * 设置用户信息
   * @description 更新用户的基本信息状态
   * @param data主要包含用户名、角色、状态等
   */
  function setUserInfo(data: { username: string; role: UserRole; user_status: string; has_card: boolean }) {
    username.value = data.username
    role.value = data.role
    // 转换为小写
    userStatus.value = data.user_status.toLowerCase() as UserStatus
    hasCard.value = data.has_card
  }

  /**
   * 用户登录
   * @description 调用登录API，成功后保存Token和用户信息
   * @param loginData 登录表单数据
   */
  async function login(loginData: LoginRequest) {
    try {
      const data = await apiLogin(loginData)
      console.log('登录成功，用户信息：', data)
      setToken(data.token)
      setUserInfo({
        username: data.username,
        role: data.role,
        // 转换为小写
        user_status: data.user_status.toLowerCase() as UserStatus,
        has_card: data.has_card
      })
      return data
    } catch (error) {
      throw error // 抛出错误供组件处理
    }
  }

  /**
   * 获取当前用户信息
   * @description 使用当前Token从服务器拉取最新用户信息
   */
  async function fetchUserInfo() {
    try {
      const user = await getCurrentUser()
      username.value = user.username
      role.value = user.role
      userStatus.value = user.status
      // 注意：getCurrentUser接口返回的User类型可能不包含has_card，视后端实现而定
      // 如果需要，可以在User类型中补充或依赖登录时的返回
    } catch (error) {
      throw error
    }
  }

  /**
   * 用户登出
   * @description 调用后端登出API（可选），并清除本地所有状态
   */
  async function logout() {
    try {
      await apiLogout()
    } catch (error) {
      console.warn('Logout API failed:', error)
    } finally {
      clearToken()
    }
  }

  /**
   * 清除 Token 和状态
   * @description 重置所有状态为初始值
   */
  function clearToken() {
    token.value = ''
    username.value = ''
    role.value = ''
    userStatus.value = ''
    hasCard.value = false
  }

  return {
    // State
    token,
    username,
    role,
    userStatus,
    hasCard,
    
    // Getters
    isLoggedIn,
    isAdmin,
    
    // Actions
    setToken,
    setUserInfo,
    login,
    fetchUserInfo,
    logout,
    clearToken
  }
}, {
  // 持久化配置：自动将State存储到localStorage
  persist: true
})

