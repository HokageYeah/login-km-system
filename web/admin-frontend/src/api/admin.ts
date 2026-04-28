import request from '@/utils/request'
import type { User, Card, Device, Statistics, UserActiveCardDetail } from '@/types'

/**
 * 批量生成卡密
 * @description 管理员批量生成卡密（需要管理员权限）
 * @param data 生成请求数据
 * @param data.app_id 所属应用ID
 * @param data.count 生成数量
 * @param data.expire_time 过期时间（ISO 8601格式）
 * @param data.max_device_count 最大可绑定设备数
 * @param data.permissions 权限列表
 * @param data.price 卡密售卖价格
 * @param data.remark 备注信息（可选）
 * @returns Promise 返回生成的卡密列表
 */
export const generateCards = (data: {
  app_id: number
  count: number
  expire_time: string
  max_device_count: number
  permissions: string[]
  price: number
  remark?: string
}) => {
  return request.post<{
    success: boolean
    message: string
    count: number
    cards: string[]
  }>('/admin/card/generate', data)
}

/**
 * 查询用户列表
 * @description 分页查询所有用户（需要管理员权限）
 * @param params 查询参数
 * @param params.page 页码（从1开始）
 * @param params.size 每页数量
 * @param params.status 用户状态筛选（可选：normal-正常，banned-封禁）
 * @param params.keyword 关键词搜索（可选，搜索用户名）
 * @returns Promise 返回用户列表
 */
export const getUserList = (params: {
  page: number
  size: number
  status?: string
  keyword?: string
}) => {
  return request.get<{
    total: number
    page: number
    size: number
    users: User[]
  }>('/admin/users', { params })
}

/**
 * 查询用户当前有效卡密详情
 * @description 查询指定用户当前有效卡密的完整信息（需要管理员权限）
 * @param userId 用户ID
 * @returns Promise 返回用户有效卡密详情
 */
export const getUserActiveCards = (userId: number) => {
  return request.get<{
    user_id: number
    username: string
    total: number
    cards: UserActiveCardDetail[]
  }>(`/admin/user/${userId}/active-cards`)
}

/**
 * 更新用户状态
 * @description 封禁或解封用户（需要管理员权限）
 * @param userId 用户ID
 * @param status 用户状态（normal-正常，banned-封禁）
 * @returns Promise 更新结果
 */
export const updateUserStatus = (userId: number, status: string) => {
  return request.post(`/admin/user/${userId}/status`, null, {
    params: { status }
  })
}

/**
 * 查询卡密列表
 * @description 分页查询所有卡密（需要管理员权限）
 * @param params 查询参数
 * @param params.page 页码（从1开始）
 * @param params.size 每页数量
 * @param params.app_id 应用ID筛选（可选）
 * @param params.status 卡密状态筛选（可选：unused-未使用，used-已使用，disabled-已禁用，expired-已过期）
 * @param params.keyword 关键词搜索（可选，搜索卡密或备注）
 * @param params.username 用户名筛选（可选）
 * @returns Promise 返回卡密列表
 */
export const getCardList = (params: {
  page: number
  size: number
  app_id?: number
  status?: string
  keyword?: string
  username?: string
}) => {
  return request.get<{
    total: number
    page: number
    size: number
    cards: Card[]
  }>('/admin/cards', { params })
}

/**
 * 更新卡密状态
 * @description 禁用或启用卡密（需要管理员权限）
 * @param cardId 卡密ID
 * @param status 卡密状态（unused-未使用，used-已使用，disabled-已禁用）
 * @returns Promise 更新结果
 */
export const updateCardStatus = (cardId: number, status: string) => {
  return request.post(`/admin/card/${cardId}/status`, { status })
}

/**
 * 更新卡密过期时间
 * @description 管理员修改卡密过期时间；是否过期由服务端按 expire_time 动态判断
 * @param cardId 卡密ID
 * @param expireTime 新的过期时间（ISO 8601格式）
 * @returns Promise 更新结果
 */
export const updateCardExpireTime = (cardId: number, expireTime: string) => {
  return request.post<{
    success: boolean
    message: string
    price?: number | string
  }>(`/admin/card/${cardId}/expire-time`, { expire_time: expireTime })
}

/**
 * 更新卡密最大设备数
 * @description 管理员修改卡密当前允许绑定的最大设备数量
 * @param cardId 卡密ID
 * @param maxDeviceCount 新的最大设备数
 * @returns Promise 更新结果
 */
export const updateCardMaxDeviceCount = (cardId: number, maxDeviceCount: number) => {
  return request.post<{
    success: boolean
    message: string
    price?: number | string
  }>(`/admin/card/${cardId}/max-device-count`, {
    max_device_count: maxDeviceCount
  })
}

/**
 * 更新卡密权限
 * @description 实时修改卡密的权限配置（需要管理员权限）
 * @param cardId 卡密ID
 * @param permissions 新的权限列表
 * @returns Promise 更新结果
 */
export const updateCardPermissions = (cardId: number, permissions: string[]) => {
  return request.post<{
    success: boolean
    message: string
    price?: number | string
  }>(`/admin/card/${cardId}/permissions`, { permissions })
}

/**
 * 查询设备列表
 * @description 分页查询所有设备（需要管理员权限）
 * @param params 查询参数
 * @param params.page 页码（从1开始）
 * @param params.size 每页数量
 * @param params.card_id 卡密ID筛选（可选）
 * @param params.user_id 用户ID筛选（可选）
 * @param params.card_key 卡密字符串筛选（可选）
 * @param params.username 用户名筛选（可选）
 * @param params.status 设备状态筛选（可选：active-激活，disabled-禁用）
 * @returns Promise 返回设备列表
 */
export const getDeviceList = (params: {
  page: number
  size: number
  card_id?: string | number
  user_id?: string | number
  card_key?: string
  username?: string
  status?: string
}) => {
  return request.get<{
    total: number
    page: number
    size: number
    devices: Device[]
  }>('/admin/devices', { params })
}

/**
 * 更新设备状态
 * @description 禁用或启用设备（需要管理员权限）
 * @param deviceId 设备ID
 * @param status 设备状态（active-激活，disabled-禁用）
 * @returns Promise 更新结果
 */
export const updateDeviceStatus = (deviceId: number, status: string) => {
  return request.post(`/admin/device/${deviceId}/status`, { status })
}

/**
 * 获取统计数据
 * @description 获取系统各项数据的统计信息（需要管理员权限）
 * @param params.start_date 收入统计开始日期（YYYY-MM-DD，可选）
 * @param params.end_date 收入统计结束日期（YYYY-MM-DD，可选）
 * @param params.trend_start_date 趋势统计开始日期（YYYY-MM-DD，可选）
 * @param params.trend_end_date 趋势统计结束日期（YYYY-MM-DD，可选）
 * @returns Promise<Statistics> 返回统计数据
 */
export const getStatistics = (params?: {
  start_date?: string
  end_date?: string
  trend_start_date?: string
  trend_end_date?: string
}) => {
  return request.get<Statistics>('/admin/statistics', { params })
}
