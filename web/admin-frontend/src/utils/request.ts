import axios, { type AxiosResponse, type AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

/**
 * API 响应数据结构
 * 与后端 ApiResponseData 格式对应
 */
export interface ApiResponse<T = any> {
  platform: string      // 平台标识
  api: string           // API 路径
  data: T              // 响应数据
  ret: string[]        // 返回状态列表
  v: number            // 版本号
}

/**
 * API 错误类
 */
export class ApiError extends Error {
  public code: string
  public api?: string
  public platform?: string
  public fullResponse?: any

  constructor(
    message: string,
    code: string,
    api?: string,
    platform?: string,
    fullResponse?: any
  ) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.api = api
    this.platform = platform
    this.fullResponse = fullResponse
  }
}

/**
 * 创建 Axios 实例
 * @description 配置基础 URL 和超时时间
 */
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,    // API 基础地址
  timeout: 10000                                  // 请求超时时间（10 秒）
})

/**
 * 请求拦截器
 * @description 在发送请求前自动添加 Token 到请求头
 */
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    // 如果用户已登录，在请求头中添加 Authorization
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

/**
 * 解析错误消息
 * @param statusCode 状态码字符串
 * @returns 解析后的错误消息
 */
const parseErrorMessage = (statusCode: string): string => {
  if (statusCode.startsWith('ERROR::')) {
    return statusCode.slice(7).trim()
  }
  if (statusCode.startsWith('SUCCESS::')) {
    return ''
  }
  return statusCode
}

/**
 * 是否为需要强制退回登录页的鉴权失效错误
 * @description 统一识别 Token 过期、Token 无效、未登录等 401 场景，
 * 避免只对某一条固定文案做脆弱判断。
 */
const isAuthExpiredError = (status: number, errorMessage: string, requestUrl?: string): boolean => {
  if (status !== 401) {
    return false
  }

  // 登录接口本身返回 401 表示账号密码错误，不应触发强制登出跳转
  if (requestUrl?.includes('/auth/login')) {
    return false
  }

  const normalizedMessage = errorMessage.trim()
  const authExpiredKeywords = [
    'Token已过期',
    'Token无效',
    '未登录',
    '认证失效',
    '登录已过期',
    '请重新登录'
  ]

  return authExpiredKeywords.some((keyword) => normalizedMessage.includes(keyword))
}

/**
 * 统一处理鉴权失效
 * @description 先提示用户，再清理本地登录态并跳转到登录页。
 */
const handleAuthExpired = async (message: string) => {
  const userStore = useUserStore()

  ElMessage.error(message || '登录已过期，请重新登录')
  userStore.clearToken()

  if (router.currentRoute.value.path !== '/login') {
    await router.push('/login')
  }
}

/**
 * 响应拦截器
 * @description 统一处理响应和错误，适配 ApiResponseData 格式
 */
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data, headers } = response

    // 检查是否为二进制数据（Blob、ArrayBuffer 等）
    const contentType = headers['content-type'] || ''
    const isBinaryData =
      data instanceof Blob ||
      data instanceof ArrayBuffer ||
      contentType.includes('image/') ||
      contentType.includes('application/octet-stream') ||
      contentType.includes('application/pdf')

    // 如果是二进制数据，直接返回
    if (isBinaryData) {
      console.log('检测到二进制数据，直接返回:', {
        type: data instanceof Blob ? 'Blob' : data instanceof ArrayBuffer ? 'ArrayBuffer' : 'Other',
        contentType,
        size: data instanceof Blob ? data.size : data instanceof ArrayBuffer ? data.byteLength : 'unknown'
      })
      return data
    }

    // 检查响应数据格式（JSON 数据）
    if (!data || typeof data !== 'object') {
      console.error('响应数据格式错误:', data)
      ElMessage.error('响应数据格式错误')
      return Promise.reject(new ApiError('响应数据格式错误', 'INVALID_RESPONSE'))
    }

    // 尝试转换为 ApiResponse 格式
    const apiData = data as ApiResponse

    // 检查 ret 字段
    if (!apiData.ret || !Array.isArray(apiData.ret) || apiData.ret.length === 0) {
      console.error('响应状态字段缺失或格式错误:', data)
      ElMessage.error('响应状态字段缺失')
      return Promise.reject(new ApiError('响应状态字段缺失', 'INVALID_RESPONSE', apiData.api, apiData.platform, data))
    }

    const statusCode = apiData.ret[0] ?? ''

    // 判断请求是否成功
    if (statusCode.startsWith('SUCCESS::')) {
      // 请求成功，直接返回 data 字段
      console.log('API 请求成功:', {
        api: apiData.api,
        platform: apiData.platform,
        data: apiData.data
      })
      return apiData.data
    } else {
      // 请求失败，解析错误信息
      const errorMsg = parseErrorMessage(statusCode)
      console.error('API 请求失败:', {
        api: apiData.api,
        platform: apiData.platform,
        statusCode,
        errorMsg,
        fullResponse: data
      })

      // 显示错误消息
      ElMessage.error(errorMsg)

      return Promise.reject(
        new ApiError(
          errorMsg,
          statusCode.split('::')[0] || 'ERROR',
          apiData.api,
          apiData.platform,
          data
        )
      )
    }
  },
  async (error: AxiosError) => {
    // HTTP 状态码错误或网络错误
    console.error('响应拦截器错误:', error)

    if (error.response) {
      // 服务器返回了错误状态码
      const { status, statusText, data } = error.response
      let errorMessage = `HTTP ${status}: ${statusText}`
      let errorCode = `HTTP_${status}`
      let api = error.config?.url ?? ''
      let platform: string | undefined

      // 尝试从响应中提取错误信息
      if (data && typeof data === 'object') {
        const apiData = data as any
        if (apiData.ret && Array.isArray(apiData.ret) && apiData.ret[0]) {
          errorMessage = parseErrorMessage(apiData.ret[0])
          errorCode = apiData.ret[0].split('::')[0] || 'ERROR'
          if (apiData.api) {
            api = apiData.api
          }
          platform = apiData.platform
        } else if (apiData.detail) {
          errorMessage = apiData.detail
        } else if (apiData.message) {
          errorMessage = apiData.message
        }
      }

      // 401: 未授权，统一处理 Token 失效类场景
      if (isAuthExpiredError(status, errorMessage, error.config?.url)) {
        await handleAuthExpired(errorMessage)
      }
      // 403: 无权限
      else if (status === 403 && errorMessage.includes('HTTP')) {
        router.push('/forbidden')                   // 跳转到 403 页面
        ElMessage.error('无权限访问')
      }
      // 其他错误
      else {
        ElMessage.error(errorMessage)
      }

      return Promise.reject(
        new ApiError(errorMessage, errorCode, api, platform, error.response)
      )
    } else if (error.request) {
      // 请求已发出但没有收到响应
      ElMessage.error('网络请求失败，请检查网络连接')
      return Promise.reject(
        new ApiError('网络请求失败，请检查网络连接', 'NETWORK_ERROR', error.config?.url ?? '')
      )
    } else {
      // 请求配置出错
      ElMessage.error(error.message || '请求配置错误')
      return Promise.reject(
        new ApiError(error.message || '请求配置错误', 'REQUEST_ERROR', error.config?.url ?? '')
      )
    }
  }
)

export default request
