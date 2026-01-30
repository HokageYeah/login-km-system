import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

/**
 * 创建Axios实例
 * @description 配置基础URL和超时时间
 */
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,    // API基础地址
  timeout: 10000                                  // 请求超时时间（10秒）
})

/**
 * 请求拦截器
 * @description 在发送请求前自动添加Token到请求头
 */
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    // 如果用户已登录，在请求头中添加Authorization
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

/**
 * 响应拦截器
 * @description 统一处理响应和错误
 */
request.interceptors.response.use(
  (response) => {
    // 检查后端自定义错误格式
    // 格式示例: { ret: ["ERROR::错误信息"], ... }
    const res = response.data
    if (res && Array.isArray(res.ret)) {
      const errorMsgs = res.ret.filter((msg: string) => msg.startsWith('ERROR::'))
      if (errorMsgs.length > 0) {
        // 提取错误信息并展示
        const msg = errorMsgs.map((m: string) => m.replace('ERROR::', '')).join('; ')
        ElMessage.error(msg)
        return Promise.reject(new Error(msg))
      }
    }
    return res
  },                    // 直接返回响应数据
  (error) => {
    // 处理 HTTP 错误响应中的业务错误信息
    if (error.response && error.response.data && Array.isArray(error.response.data.ret)) {
      const errorMsgs = error.response.data.ret.filter((msg: string) => msg.startsWith('ERROR::'))
      if (errorMsgs.length > 0) {
        const msg = errorMsgs.map((m: string) => m.replace('ERROR::', '')).join('; ')
        ElMessage.error(msg)
        return Promise.reject(error)
      }
    }

    // 401: 未授权，Token过期或无效
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.clearToken()                      // 清除本地Token
      router.push('/login')                       // 跳转到登录页
      ElMessage.error('登录已过期，请重新登录')
    } 
    // 403: 无权限
    else if (error.response?.status === 403) {
      router.push('/forbidden')                   // 跳转到403页面
      ElMessage.error('无权限访问')
    } 
    // 其他错误
    else {
      ElMessage.error(error.response?.data?.detail || error.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request
