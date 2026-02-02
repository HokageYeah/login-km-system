```html
<template>
  <el-dialog
    v-model="dialogVisible"
    title="修改卡密权限"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="card" class="permission-dialog">
      <!-- 卡密信息 -->
      <div class="card-info">
        <div class="info-item">
          <span class="info-label">卡密：</span>
          <span class="info-value">{{ card.card_key }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">状态：</span>
          <el-tag :type="getStatusType(card.status)" size="small">
            {{ getStatusText(card.status) }}
          </el-tag>
        </div>
      </div>

      <!-- 权限选择 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="permission-form"
      >
        <el-form-item label="权限配置" prop="permissions">
          <div v-loading="loadingPermissions" class="permission-container">
            <el-checkbox-group v-model="form.permissions" class="permission-group">
              <template v-if="availablePermissions.length > 0">
                <div
                  v-for="permission in availablePermissions"
                  :key="permission.permission_key"
                  class="permission-card"
                  :class="{
                    'permission-card-checked': form.permissions.includes(permission.permission_key),
                    'permission-card-disabled': permission.status === 'disabled'
                  }"
                >
                  <el-checkbox
                    :label="permission.permission_key"
                    :disabled="permission.status === 'disabled'"
                    class="permission-checkbox"
                  >
                    <div class="checkbox-content">
                      <div class="checkbox-header">
                        <el-icon v-if="permission.icon" class="checkbox-icon">
                          <component :is="getIconComponent(permission.icon)" />
                        </el-icon>
                        <span class="checkbox-label">{{ permission.permission_key }}</span>
                        <span class="checkbox-label">{{ `(${permission.permission_name})` }}</span>
                        <el-tag v-if="permission.category" size="small" type="info" class="category-tag">
                          {{ permission.category }}
                        </el-tag>
                      </div>
                      <!-- <span class="checkbox-desc">{{ permission.description || '暂无描述' }}</span> -->
                    </div>
                  </el-checkbox>
                </div>
              </template>
              <el-empty v-else description="暂无可用权限" />
            </el-checkbox-group>
          </div>
        </el-form-item>
      </el-form>

      <!-- 提示信息 -->
      <el-alert
        title="权限修改将立即生效"
        type="warning"
        :closable="false"
        show-icon
        class="mt-4"
      >
        <template #default>
          修改权限后，使用该卡密的用户将立即获得或失去相应权限
        </template>
      </el-alert>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleSubmit"
        >
          确定修改
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
/**
 * 修改权限弹窗组件
 * @description 修改卡密的权限配置，从后端动态加载可用权限列表
 */
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { getCardFeaturePermissions, updateCardFeaturePermissions } from '@/api/feature-permission'
import type { Card, FeaturePermission } from '@/types'

/**
 * Props 定义
 */
interface Props {
  modelValue: boolean           // 弹窗显示状态
  card: Card | null             // 卡密信息
  permissions?: string[]        // 已有的权限列表（用于默认选中）
}

const props = defineProps<Props>()

/**
 * Emits 定义
 */
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

/**
 * 弹窗显示状态（双向绑定）
 */
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

/**
 * 状态定义
 */
const loading = ref(false)                              // 提交加载状态
const loadingPermissions = ref(false)                    // 加载权限列表状态
const formRef = ref<FormInstance>()                     // 表单引用
const availablePermissions = ref<FeaturePermission[]>([])  // 可用权限列表

/**
 * 表单数据
 */
const form = reactive({
  permissions: [] as string[]
})

/**
 * 表单验证规则
 */
const rules: FormRules = {
  permissions: [
    { required: true, message: '请至少选择一项权限', trigger: 'change', type: 'array', min: 1 }
  ]
}

/**
 * 获取状态标签类型
 * @param status 卡密状态
 * @returns Element Plus Tag 类型
 */
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    unused: 'success',
    used: 'warning',
    disabled: 'danger'
  }
  return typeMap[status] || 'info'
}

/**
 * 获取状态文本
 * @param status 卡密状态
 * @returns 状态中文文本
 */
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    unused: '未使用',
    used: '已使用',
    disabled: '已禁用'
  }
  return textMap[status] || status
}

/**
 * 获取图标组件
 * @param iconName 图标名称
 * @returns 图标组件
 */
const getIconComponent = (iconName: string) => {
  // 这里可以根据实际的图标名称返回对应的组件
  // 暂时返回 null，如果需要可以添加实际的图标映射
  return null
}

/**
 * 处理卡片点击
 * @param permissionKey 权限标识
 * @param status 权限状态
 */
const handleCardClick = (permissionKey: string, status: string) => {
  // 如果权限被禁用，不允许切换
  if (status === 'disabled') return

  const index = form.permissions.indexOf(permissionKey)
  if (index > -1) {
    // 已选中，取消选中
    form.permissions.splice(index, 1)
  } else {
    // 未选中，添加选中
    form.permissions.push(permissionKey)
  }
}

/**
 * 加载卡密权限数据
 */
const loadCardPermissions = async () => {
  if (!props.card) return

  loadingPermissions.value = true
  try {
    const response = await getCardFeaturePermissions(props.card.id)
    // 设置可用权限列表
    availablePermissions.value = response.available_permissions || []
    
    // 优先使用 props 传入的权限，其次使用 API 返回的权限
    if (props.permissions && props.permissions.length > 0) {
      form.permissions = [...props.permissions]
    } else {
      form.permissions = response.permission_keys || []
    }
  } catch (error: any) {
    console.error('加载卡密权限失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('加载权限列表失败')
    }
  } finally {
    loadingPermissions.value = false
  }
}

/**
 * 处理提交
 */
const handleSubmit = async () => {
  if (!formRef.value || !props.card) return

  try {
    // 验证表单
    await formRef.value.validate()

    loading.value = true

    // 调用更新权限 API
    await updateCardFeaturePermissions(props.card.id, form.permissions)

    ElMessage.success('权限修改成功')
    emit('success')
    handleClose()
  } catch (error: any) {
    console.error('修改权限失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('修改失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 处理关闭弹窗
 */
const handleClose = () => {
  dialogVisible.value = false
}

/**
 * 监听弹窗打开，加载权限列表
 * NOTE: 只在弹窗打开时加载，避免重复调用接口
 */
watch(dialogVisible, (newVal) => {
  if (newVal && props.card) {
    // 弹窗打开时加载权限
    loadCardPermissions()
  }

  // 监听弹窗关闭，重置表单
  if (!newVal && formRef.value) {
    setTimeout(() => {
      formRef.value?.resetFields()
      availablePermissions.value = []
    }, 300)
  }
})
</script>

<style scoped>
.permission-dialog {
  padding: 16px 0;
}

/* 卡密信息 */
.card-info {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  display: flex;
  gap: 24px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  font-size: 14px;
  color: #666;
}

.info-value {
  font-size: 14px;
  font-family: monospace;
  font-weight: 500;
  color: #333;
}

/* 权限表单 */
.permission-form {
  margin-bottom: 0;
}

.permission-container {
  width: 100%;
  min-height: 100px;
}

.permission-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

/* 简洁权限卡片样式 */
.permission-card {
  width: 100%;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.permission-card:hover {
  border-color: #409eff;
  background-color: #f0f7ff;
}

/* 选中状态 */
.permission-card-checked {
  border-color: #409eff;
  background-color: #ecf5ff;
}

/* 禁用状态 */
.permission-card-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #fafafa;
}

.permission-card-disabled:hover {
  border-color: #e0e0e0;
  background-color: #fafafa;
}

/* 复选框样式 */
.permission-checkbox {
  width: 100%;
  padding: 12px 16px;
  margin: 0;
}

:deep(.el-checkbox__label) {
  width: 100%;
}

/* 复选框内容 */
.checkbox-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.checkbox-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.checkbox-icon {
  color: #409eff;
  font-size: 18px;
}

.checkbox-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.permission-card-checked .checkbox-label {
  color: #409eff;
}

.category-tag {
  font-size: 12px;
}

.checkbox-desc {
  font-size: 13px;
  color: #999;
  line-height: 1.5;
  margin-top: 4px;
}

/* 滚动条样式 */
.permission-group::-webkit-scrollbar {
  width: 6px;
}

.permission-group::-webkit-scrollbar-track {
  background-color: #f0f0f0;
  border-radius: 3px;
}

.permission-group::-webkit-scrollbar-thumb {
  background-color: #d0d0d0;
  border-radius: 3px;
}

.permission-group::-webkit-scrollbar-thumb:hover {
  background-color: #b0b0b0;
}

/* 对话框底部按钮 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 优化复选框原始样式 */
:deep(.el-checkbox__input) {
  transition: all 0.2s;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #409eff;
  border-color: #409eff;
}

:deep(.el-checkbox__inner) {
  width: 16px;
  height: 16px;
}

:deep(.el-checkbox__input:hover .el-checkbox__inner) {
  border-color: #409eff;
}

/* Empty 状态 */
:deep(.el-empty) {
  padding: 32px 0;
}
</style>
```
