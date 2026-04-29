import type { Statistics } from '@/types'

const DEFAULT_TREND_DAYS = 7

/**
 * 生成最近 N 天的日期标签
 * @description 仪表盘首屏兜底时统一使用这一套日期格式，
 * 避免两个页面各自生成标签导致口径不一致。
 */
const buildFallbackLabels = (days: number) => {
  return Array.from({ length: days }, (_, index) => {
    const date = new Date()
    date.setDate(date.getDate() - (days - 1 - index))
    return `${String(date.getMonth() + 1).padStart(2, '0')}月${String(date.getDate()).padStart(2, '0')}日`
  })
}

/**
 * 创建仪表盘统计兜底结构
 * @description 统一给多个仪表盘页面使用，避免页面在接口未返回时出现空引用。
 */
export const createDashboardFallbackStatistics = (
  days: number = DEFAULT_TREND_DAYS
): Statistics => {
  return {
    users: { total: 0, normal: 0, banned: 0 },
    cards: { total: 0, unused: 0, used: 0, disabled: 0 },
    devices: { total: 0, active: 0, disabled: 0 },
    apps: { total: 0, active: 0 },
    revenue: { total: 0, used: 0, unused: 0 },
    all_time_revenue: { total: 0, used: 0, unused: 0 },
    revenue_range: {
      start_date: new Date().toISOString().slice(0, 10),
      end_date: new Date().toISOString().slice(0, 10)
    },
    trend_range: {
      start_date: new Date().toISOString().slice(0, 10),
      end_date: new Date().toISOString().slice(0, 10)
    },
    trends: {
      labels: buildFallbackLabels(days),
      daily_new: {
        users: Array(days).fill(0),
        devices: Array(days).fill(0),
        cards: Array(days).fill(0),
        apps: Array(days).fill(0)
      },
      cumulative: {
        users: Array(days).fill(0),
        devices: Array(days).fill(0),
        cards: Array(days).fill(0),
        apps: Array(days).fill(0)
      }
    },
    sales_trend: {
      labels: buildFallbackLabels(days),
      daily_orders: Array(days).fill(0),
      daily_revenue: Array(days).fill(0),
      average_order_value: Array(days).fill(0)
    },
    permission_revenue: []
  }
}

/**
 * 数值格式化
 * @description 统一用中文数字分隔格式，便于多个页面保持一致显示。
 */
export const formatDashboardNumber = (num: number) => {
  return num.toLocaleString('zh-CN')
}

export const toDashboardAmount = (value: number | string | null | undefined) => {
  const parsedValue = Number(value ?? 0)
  return Number.isFinite(parsedValue) ? parsedValue : 0
}

export const formatDashboardCurrency = (value: number | string | null | undefined) => {
  return `¥${toDashboardAmount(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`
}

/**
 * 计算百分比
 * @description 用在各种健康度、占比、完成度场景中。
 */
export const getRate = (value: number, total: number) => {
  if (!total) return 0
  return Math.round((value / total) * 100)
}

/**
 * 获取序列最后一个值
 */
export const getLastValue = (values: number[]) => {
  if (!values.length) return 0
  return values[values.length - 1] ?? 0
}

/**
 * 获取序列平均值
 */
export const getAverageValue = (values: number[]) => {
  if (!values.length) return 0
  const total = values.reduce((sum, current) => sum + current, 0)
  return Math.round((total / values.length) * 10) / 10
}

/**
 * 获取序列总和
 */
export const getSeriesTotal = (values: number[]) => {
  return values.reduce((sum, current) => sum + current, 0)
}

/**
 * 获取序列峰值
 */
export const getSeriesPeak = (values: number[]) => {
  if (!values.length) return 0
  return Math.max(...values)
}

/**
 * 对百分比做范围收敛
 * @description 某些联动指标是由比值推导而来，可能超过 100%，
 * 页面展示时统一收敛到 0-100 范围，便于做进度条和仪表盘。
 */
export const clampPercent = (value: number) => {
  if (!Number.isFinite(value)) return 0
  return Math.max(0, Math.min(100, Math.round(value)))
}
