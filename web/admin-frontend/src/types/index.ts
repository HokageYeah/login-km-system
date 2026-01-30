// ==================== 用户相关类型 ====================

/**
 * 用户角色类型
 * @description 定义用户在系统中的角色
 */
export type UserRole = 'admin' | 'user' // admin: 管理员，user: 普通用户

/**
 * 用户状态类型
 * @description 定义用户账号的状态
 */
export type UserStatus = 'normal' | 'banned' // normal: 正常，banned: 封禁

/**
 * 用户信息接口
 * @description 用户的基本信息
 */
export interface User {
  id: number                    // 用户ID
  username: string              // 用户名
  status: UserStatus            // 用户状态
  role: UserRole                // 用户角色
  created_at: string            // 创建时间（ISO 8601格式）
  last_login_at?: string        // 最后登录时间（可选）
}

/**
 * 登录请求接口
 * @description 用户登录时提交的数据
 */
export interface LoginRequest {
  username: string              // 用户名
  password: string              // 密码
  app_key: string               // 应用标识（必填）
  device_id: string            // 设备ID（必填，用于多设备管理）
}

/**
 * 登录响应接口
 * @description 登录成功后服务器返回的数据
 */
export interface LoginResponse {
  token: string                 // JWT Token，用于后续API认证
  user_status: UserStatus       // 用户状态
  has_card: boolean             // 是否已绑定卡密
  username: string              // 用户名
  role: UserRole                // 用户角色
}

// ==================== 应用相关类型 ====================

/**
 * 应用状态类型
 * @description 定义应用的启用状态
 */
export type AppStatus = 'normal' | 'disabled' // normal: 正常，disabled: 禁用

/**
 * 应用信息接口
 * @description 应用的基本信息
 */
export interface App {
  id: number                    // 应用ID
  app_key: string               // 应用唯一标识
  app_name: string              // 应用名称
  status: AppStatus             // 应用状态
  created_at: string            // 创建时间
}

// ==================== 卡密相关类型 ====================

/**
 * 卡密状态类型
 * @description 定义卡密的使用状态
 */
export type CardStatus = 'unused' | 'used' | 'disabled' 
// unused: 未使用，used: 已使用，disabled: 已禁用

/**
 * 卡密信息接口
 * @description 卡密的详细信息
 */
export interface Card {
  id: number                    // 数据库ID
  card_id: number               // 卡密ID
  card_key: string              // 卡密字符串（格式：XXXX-XXXX-XXXX-XXXX）
  app_name?: string             // 所属应用名称（可选）
  status: CardStatus            // 卡密状态
  expire_time: string           // 过期时间（ISO 8601格式）
  max_device_count: number      // 最大可绑定设备数
  permissions: string[]         // 权限列表
  bind_devices?: number         // 已绑定设备数（可选）
  remark?: string               // 备注信息（可选）
  created_at: string            // 创建时间
}

// ==================== 设备相关类型 ====================

/**
 * 设备信息接口
 * @description 绑定设备的详细信息
 */
export interface Device {
  id: number                    // 设备记录ID
  card_id: number               // 关联的卡密ID
  card_key: string              // 关联的卡密字符串
  user_id?: number              // 关联的用户ID（可选）
  username?: string             // 关联的用户名（可选）
  device_id: string             // 设备唯一标识
  device_name?: string          // 设备名称（可选）
  bind_time: string             // 绑定时间
  last_active_at: string        // 最后活跃时间
  status: 'active' | 'disabled' // 设备状态：active-激活，disabled-禁用
}

// ==================== 统计数据类型 ====================

/**
 * 统计数据接口
 * @description 系统各项数据的统计信息
 */
export interface Statistics {
  total_users: number           // 用户总数
  total_cards: number           // 卡密总数
  unused_cards: number          // 未使用卡密数
  used_cards: number            // 已使用卡密数
  disabled_cards: number        // 已禁用卡密数
  total_devices: number         // 设备总数
  active_devices: number        // 活跃设备数
  total_apps: number            // 应用总数
  normal_apps: number           // 正常应用数
  today_new_users: number       // 今日新增用户数
  today_new_cards: number       // 今日新增卡密数
}

// ==================== 分页相关类型 ====================

/**
 * 分页参数接口
 * @description 列表查询时的分页参数
 */
export interface PaginationParams {
  page: number                  // 页码（从1开始）
  size: number                  // 每页数量
}

/**
 * 分页响应接口
 * @description 分页列表的响应结构
 */
export interface PaginationResponse<T> {
  total: number                 // 总记录数
  page: number                  // 当前页码
  size: number                  // 每页数量
  data: T[]                     // 数据列表
}

// ==================== 通用响应类型 ====================

/**
 * 通用成功响应接口
 * @description API操作成功的通用响应结构
 */
export interface SuccessResponse {
  success: boolean              // 操作是否成功
  message: string               // 提示信息
}

/**
 * 通用错误响应接口
 * @description API操作失败的错误响应结构
 */
export interface ErrorResponse {
  detail: string                // 错误详情
  status_code?: number          // HTTP状态码（可选）
}
