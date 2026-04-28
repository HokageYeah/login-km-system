import type { FeaturePermission } from '@/types'

export const BASE_DEVICE_COUNT = 3
export const EXTRA_DEVICE_PRICE = 0.5
export const MONTH_PRICE_DAYS = 30
export const MIN_CARD_PRICE = 0.5

export interface CardPricingBreakdown {
  monthlyPermissionPrice: number
  proratedPermissionPrice: number
  extraDevicePrice: number
  durationDays: number
  finalPrice: number
}

export const formatPrice = (price: number | string | null | undefined) => {
  const parsedPrice = Number(price ?? 0)
  if (Number.isNaN(parsedPrice)) {
    return '¥0.00'
  }
  return `¥${parsedPrice.toFixed(2)}`
}

export const extractPermissionKeys = (permissions: unknown): string[] => {
  if (Array.isArray(permissions)) {
    return permissions.map(String).filter(Boolean)
  }

  if (typeof permissions === 'object' && permissions !== null) {
    return Object.entries(permissions)
      .filter(([, value]) => value === true || String(value).toLowerCase() === 'true')
      .map(([permissionKey]) => permissionKey)
      .filter(Boolean)
  }

  return []
}

const getDurationDays = (expireTime: string) => {
  if (!expireTime) {
    return MONTH_PRICE_DAYS
  }

  const expireTimestamp = new Date(expireTime).getTime()
  const nowTimestamp = Date.now()
  if (Number.isNaN(expireTimestamp) || expireTimestamp <= nowTimestamp) {
    return 1
  }

  return Math.max(1, Math.ceil((expireTimestamp - nowTimestamp) / (24 * 60 * 60 * 1000)))
}

export const calculateCardPricingBreakdown = (params: {
  permissions: unknown
  availablePermissions: FeaturePermission[]
  expireTime: string
  maxDeviceCount: number
}): CardPricingBreakdown => {
  const selectedKeys = new Set(extractPermissionKeys(params.permissions))
  const monthlyPermissionPrice = params.availablePermissions.reduce((total, permission) => {
    if (!selectedKeys.has(permission.permission_key)) {
      return total
    }

    const permissionPrice = Number(permission.price ?? 0)
    return total + (Number.isNaN(permissionPrice) ? 0 : permissionPrice)
  }, 0)

  const extraDeviceCount = Math.max(0, Number(params.maxDeviceCount || 0) - BASE_DEVICE_COUNT)
  const extraDevicePrice = extraDeviceCount * EXTRA_DEVICE_PRICE
  const durationDays = getDurationDays(params.expireTime)
  const proratedPermissionPrice = (monthlyPermissionPrice / MONTH_PRICE_DAYS) * durationDays
  const rawPrice = proratedPermissionPrice + extraDevicePrice
  const finalPrice = Math.max(MIN_CARD_PRICE, rawPrice)

  return {
    monthlyPermissionPrice: Number(monthlyPermissionPrice.toFixed(2)),
    proratedPermissionPrice: Number(proratedPermissionPrice.toFixed(2)),
    extraDevicePrice: Number(extraDevicePrice.toFixed(2)),
    durationDays,
    finalPrice: Number(finalPrice.toFixed(2))
  }
}
