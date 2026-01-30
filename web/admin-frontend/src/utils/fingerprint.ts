import FingerprintJS from '@fingerprintjs/fingerprintjs'

/**
 * 获取浏览器指纹作为设备ID
 * @description 使用FingerprintJS生成唯一且稳定的设备标识符
 * @returns Promise<string> 设备唯一标识
 */
export async function getDeviceId(): Promise<string> {
  try {
    // 加载FingerprintJS
    const fp = await FingerprintJS.load()
    
    // 获取访问者标识
    const result = await fp.get()
    
    // 返回访问者ID（每个浏览器唯一且稳定）
    return result.visitorId
  } catch (error) {
    console.error('Failed to generate device fingerprint:', error)
    // 降级方案：生成一个基于时间戳和随机数的ID，并存储在localStorage
    let fallbackId = localStorage.getItem('device_id_fallback')
    if (!fallbackId) {
      fallbackId = `fallback_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`
      localStorage.setItem('device_id_fallback', fallbackId)
    }
    return fallbackId
  }
}
