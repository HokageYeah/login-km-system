import request from '@/utils/request'
import type { LoginRequest, LoginResponse, User } from '@/types'

/**
 * 用户登录
 * @param data 登录请求数据
 * @returns Promise<LoginResponse> 返回token和用户信息
 */
export const login = (data: LoginRequest) => {
  return request.post<any, LoginResponse>('/auth/login', data)
}

/**
 * 用户注册
 * @param data 注册请求数据（用户名和密码）
 * @returns Promise<User> 返回新注册的用户信息
 */
export const register = (data: { username: string; password: string }) => {
  return request.post<any, User>('/auth/register', data)
}

/**
 * 获取当前登录用户信息
 * @returns Promise<User> 返回当前用户详细信息
 */
export const getCurrentUser = () => {
  return request.get<any, User>('/auth/me')
}

/**
 * 用户登出
 * @returns Promise<void> 登出成功后无返回值
 */
export const logout = () => {
  return request.post<any, void>('/auth/logout')
}

/**
 * 获取公开应用列表
 * @returns Promise<{ total: number, apps: Array<{ app_key: string, app_name: string }> }>
 */
export const getPublicApps = () => {
    return request.get<any, { total: number, apps: Array<{ app_key: string, app_name: string }> }>('/app/public/list')
}
