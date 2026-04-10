import request from '@/utils/request'
import type { FeaturePermission, SuccessResponse } from '@/types'

/**
 * 查询功能权限列表
 * @description 分页查询所有功能权限（需要管理员权限）
 * @param params 查询参数
 * @param params.page 页码（从1开始）
 * @param params.size 每页数量
 * @param params.category 分类筛选（可选）
 * @param params.status 状态筛选（可选）
 * @param params.keyword 关键词搜索（可选，搜索权限标识、权限名称）
 * @returns Promise 返回功能权限列表
 */
export const getFeaturePermissionList = (params: {
  page: number
  size: number
  category?: string
  status?: string
  keyword?: string
}) => {
  return request.get<{
    total: number
    permissions: FeaturePermission[]
  }>('/admin/feature-permissions/list', { params })
}

/**
 * 查询权限分类列表
 * @description 查询所有权限分类（需要管理员权限）
 * @returns Promise 返回分类列表
 */
export const getPermissionCategories = () => {
  return request.get<{
    total: number
    categories: string[]
  }>('/admin/feature-permissions/categories')
}

/**
 * 创建功能权限
 * @description 创建新的功能权限（需要管理员权限）
 * @param data 创建请求数据
 * @param data.permission_key 权限标识（如：wechat, ximalaya），必须唯一
 * @param data.permission_name 权限名称（如：微信抓取、喜马拉雅播放）
 * @param data.description 权限描述（可选）
 * @param data.category 权限分类（可选，如：数据抓取、媒体播放）
 * @param data.icon 图标（可选）
 * @param data.sort_order 排序，数字越小越靠前
 * @returns Promise 创建结果
 */
export const createFeaturePermission = (data: {
  permission_key: string
  permission_name: string
  description?: string
  category?: string
  icon?: string
  sort_order?: number
}) => {
  return request.post<{
    success: boolean
    message: string
    permission: FeaturePermission
  }>('/admin/feature-permissions/create', data)
}

/**
 * 更新功能权限
 * @description 更新功能权限信息（需要管理员权限）
 * @param permissionId 功能权限ID
 * @param data 更新请求数据
 * @returns Promise 更新结果
 */
export const updateFeaturePermission = (
  permissionId: number,
  data: {
    permission_key?: string
    permission_name?: string
    description?: string
    category?: string
    icon?: string
    sort_order?: number
    status?: string
  }
) => {
  return request.post<{
    success: boolean
    message: string
    permission: FeaturePermission
  }>(`/admin/feature-permissions/update/${permissionId}`, data)
}

/**
 * 删除功能权限
 * @description 删除功能权限（需要管理员权限）
 * @param permissionId 功能权限ID
 * @returns Promise 删除结果
 */
export const deleteFeaturePermission = (permissionId: number) => {
  return request.post<SuccessResponse>(`/admin/feature-permissions/delete/${permissionId}`)
}

/**
 * 查询卡密功能权限
 * @description 查询指定卡密的功能权限列表（需要管理员权限）
 * @param cardId 卡密ID
 * @returns Promise 返回卡密的权限和所有可用权限
 */
export const getCardFeaturePermissions = (cardId: number) => {
  return request.get<{
    card_id: number
    permission_keys: string[]
    available_permissions: FeaturePermission[]
  }>(`/admin/feature-permissions/card/${cardId}/permissions`)
}

/**
 * 更新卡密功能权限
 * @description 更新卡密的功能权限配置（需要管理员权限）
 * @param cardId 卡密ID
 * @param permissionKeys 权限标识列表
 * @returns Promise 更新结果
 */
export const updateCardFeaturePermissions = (cardId: number, permissionKeys: string[]) => {
  return request.post<{
    success: boolean
    message: string
    permissions: string[]
  }>(`/admin/feature-permissions/card/${cardId}/update-permissions`, {
    permission_keys: permissionKeys
  })
}
