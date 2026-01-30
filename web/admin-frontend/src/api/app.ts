import request from '@/utils/request'
import type { App } from '@/types'

/**
 * 查询应用列表
 * @description 获取系统中所有应用的列表（需要管理员权限）
 * @returns Promise<{total: number, apps: App[]}> 返回应用列表
 */
export const getAppList = () => {
  return request.get<{ total: number; apps: App[] }>('/app/list')
}

/**
 * 创建新应用
 * @description 创建一个新的应用（需要管理员权限）
 * @param data 创建请求数据
 * @param data.app_name 应用名称
 * @param data.app_key 应用标识（可选，不填则自动生成）
 * @returns Promise 创建结果
 */
export const createApp = (data: {
  app_name: string
  app_key?: string
}) => {
  return request.post('/app/create', data)
}

/**
 * 更新应用状态
 * @description 启用或禁用应用（需要管理员权限）
 * @param appId 应用ID
 * @param status 应用状态（normal-正常，disabled-禁用）
 * @returns Promise 更新结果
 */
export const updateAppStatus = (appId: number, status: string) => {
  return request.post(`/app/${appId}/status`, { status })
}

/**
 * 查询应用详情
 * @description 获取指定应用的详细信息（需要管理员权限）
 * @param appId 应用ID
 * @returns Promise<App> 返回应用详情
 */
export const getAppDetail = (appId: number) => {
  return request.get<App>(`/app/${appId}`)
}
