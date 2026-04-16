/**
 * 过期时间快捷选项工具
 * @description 统一维护“1天 / 1周 / 1个月 / 1季度 / 1年”的快捷时间计算逻辑，
 * 避免生成卡密、修改过期时间等多个界面各自维护一套时间偏移实现，导致后续规则漂移。
 */

export type ExpireShortcutKey = 'oneDay' | 'oneWeek' | 'oneMonth' | 'oneQuarter' | 'oneYear'

export interface ExpireShortcutOption {
  key: ExpireShortcutKey
  label: string
}

/**
 * 统一的快捷时间选项定义
 * @description 这里只维护展示文案和唯一 key，具体时间值在点击时按“当前时间”动态计算，
 * 确保每次选择都以用户操作当下的系统时间为基准。
 */
export const EXPIRE_SHORTCUT_OPTIONS: ExpireShortcutOption[] = [
  { key: 'oneDay', label: '1天' },
  { key: 'oneWeek', label: '1周' },
  { key: 'oneMonth', label: '1个月' },
  { key: 'oneQuarter', label: '1个季度' },
  { key: 'oneYear', label: '1年' }
]

const padDatePart = (value: number) => String(value).padStart(2, '0')

/**
 * 将 Date 转成后端和页面统一使用的时间字符串
 * @param date Date 对象
 * @returns YYYY-MM-DDTHH:mm:ss
 */
export const formatDateTimeValue = (date: Date) => {
  const year = date.getFullYear()
  const month = padDatePart(date.getMonth() + 1)
  const day = padDatePart(date.getDate())
  const hours = padDatePart(date.getHours())
  const minutes = padDatePart(date.getMinutes())
  const seconds = padDatePart(date.getSeconds())

  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
}

/**
 * 基于“自然月”增加月份，并自动处理月底溢出问题
 * @description 例如 1 月 31 日 + 1 个月，应落到 2 月最后一天，而不是跳到 3 月。
 * @param baseDate 基准时间
 * @param months 增加月数
 * @returns 新的日期对象
 */
const addMonthsSafely = (baseDate: Date, months: number) => {
  const result = new Date(baseDate)
  const targetMonthIndex = result.getMonth() + months
  const targetYear = result.getFullYear() + Math.floor(targetMonthIndex / 12)
  const normalizedMonth = ((targetMonthIndex % 12) + 12) % 12
  const originalDay = result.getDate()

  const maxDayInTargetMonth = new Date(targetYear, normalizedMonth + 1, 0).getDate()
  const safeDay = Math.min(originalDay, maxDayInTargetMonth)

  result.setFullYear(targetYear, normalizedMonth, safeDay)
  return result
}

/**
 * 计算快捷过期时间
 * @param shortcutKey 快捷选项 key
 * @param now 基准时间，默认取当前时间；预留该参数主要是为了后续测试和扩展更方便
 * @returns 计算后的时间字符串
 */
export const getExpireShortcutValue = (
  shortcutKey: ExpireShortcutKey,
  now: Date = new Date()
) => {
  const targetDate = new Date(now)

  switch (shortcutKey) {
    case 'oneDay':
      targetDate.setDate(targetDate.getDate() + 1)
      break
    case 'oneWeek':
      targetDate.setDate(targetDate.getDate() + 7)
      break
    case 'oneMonth':
      return formatDateTimeValue(addMonthsSafely(targetDate, 1))
    case 'oneQuarter':
      return formatDateTimeValue(addMonthsSafely(targetDate, 3))
    case 'oneYear':
      return formatDateTimeValue(addMonthsSafely(targetDate, 12))
    default:
      return formatDateTimeValue(targetDate)
  }

  return formatDateTimeValue(targetDate)
}
