import type { Directive } from 'vue'
import { useUserStore } from '@/stores/user'

/**
 * 权限指令
 * @description 用于按钮级别的权限控制
 * @example <el-button v-permission="['admin']">删除</el-button>
 */
export const permission: Directive = {
  mounted(el, binding) {
    const userStore = useUserStore()
    const { value } = binding                 // 获取指令绑定的值（允许的角色数组）
    
    // 如果当前用户角色不在允许的角色列表中，则移除该元素
    if (value && value instanceof Array && value.length > 0) {
      if (!value.includes(userStore.role)) {
        el.parentNode?.removeChild(el)
      }
    } else {
      throw new Error(`need roles! Like v-permission="['admin','editor']"`)
    }
  }
}
