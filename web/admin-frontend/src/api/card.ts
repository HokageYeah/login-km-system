import request from '@/utils/request'
import type { Card, Device } from '@/types'

/**
 * 查询我的卡密列表
 * @description 获取当前用户已绑定的所有卡密
 * @returns Promise<{has_card: boolean, cards: Card[]}> 返回卡密列表
 */
export const getMyCards = () => {
  return request.get<{ has_card: boolean; cards: Card[] }>('/card/my')
}

/**
 * 绑定卡密到当前账号和设备
 * @param data 绑定请求数据
 * @param data.card_key 卡密字符串
 * @param data.device_id 设备唯一标识
 * @param data.device_name 设备名称（可选）
 * @returns Promise 绑定结果
 */
export const bindCard = (data: {
  card_key: string
  device_id: string
  device_name?: string
}) => {
  return request.post('/card/bind', data)
}

/**
 * 解绑设备
 * @description 将指定设备从卡密中解绑
 * @param data 解绑请求数据
 * @param data.card_id 卡密ID
 * @param data.device_id 设备ID
 * @returns Promise 解绑结果
 */
export const unbindDevice = (data: {
  card_id: number
  device_id: string
}) => {
  return request.post('/card/unbind-device', data)
}

/**
 * 查询卡密详情
 * @description 获取指定卡密的详细信息和绑定设备列表
 * @param cardId 卡密ID
 * @returns Promise<{card: Card, devices: Device[]}> 返回卡密详情和设备列表
 */
export const getCardDetail = (cardId: number) => {
  return request.get<{
    card: Card
    devices: Device[]
  }>(`/card/${cardId}`)
}

/**
 * 批量删除卡密
 * @description 批量删除指定的卡密（需要管理员权限）
 * @param cardIds 要删除的卡密ID列表
 * @returns Promise 删除结果
 */
export const batchDeleteCards = (cardIds: number[]) => {
  return request.post('/card/batch-delete', cardIds)
}
