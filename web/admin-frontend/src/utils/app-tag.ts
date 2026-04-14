/**
 * 根据应用标识生成稳定的标签颜色。
 *
 * 设计说明：
 * - 同一个应用在不同页面必须保持相同颜色，避免管理员在应用页、卡密页、权限页之间切换时认知断裂；
 * - 颜色由稳定哈希计算得出，不依赖后端额外配置，避免为展示问题增加数据库设计复杂度。
 */
const APP_TAG_STYLES = [
  { background: '#eff6ff', border: '#bfdbfe', color: '#1d4ed8' },
  { background: '#ecfeff', border: '#a5f3fc', color: '#0f766e' },
  { background: '#f0fdf4', border: '#bbf7d0', color: '#15803d' },
  { background: '#fff7ed', border: '#fed7aa', color: '#c2410c' },
  { background: '#fef2f2', border: '#fecaca', color: '#b91c1c' },
  { background: '#faf5ff', border: '#e9d5ff', color: '#7e22ce' },
  { background: '#fdf4ff', border: '#f5d0fe', color: '#a21caf' },
  { background: '#fefce8', border: '#fde68a', color: '#a16207' }
]

const hashText = (text: string) => {
  let hash = 0
  for (let index = 0; index < text.length; index += 1) {
    hash = (hash * 31 + text.charCodeAt(index)) >>> 0
  }
  return hash
}

export const getAppTagStyle = (appKey?: string, appName?: string) => {
  const source = (appKey || appName || 'unknown_app').trim()
  const styleIndex = hashText(source) % APP_TAG_STYLES.length
  return APP_TAG_STYLES[styleIndex]
}
