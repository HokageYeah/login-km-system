<template>
  <el-dialog
    v-model="dialogVisible"
    title="修改卡密权限"
    width="500px"
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
          <el-checkbox-group v-model="form.permissions" class="permission-group">
            <el-checkbox label="basic" class="permission-checkbox">
              <div class="checkbox-content">
                <span class="checkbox-label">基础功能</span>
                <span class="checkbox-desc">访问基本功能模块</span>
              </div>
            </el-checkbox>
            <el-checkbox label="advanced" class="permission-checkbox">
              <div class="checkbox-content">
                <span class="checkbox-label">高级功能</span>
                <span class="checkbox-desc">访问高级功能模块</span>
              </div>
            </el-checkbox>
            <el-checkbox label="admin" class="permission-checkbox">
              <div class="checkbox-content">
                <span class="checkbox-label">管理功能</span>
                <span class="checkbox-desc">访问管理功能模块</span>
              </div>
            </el-checkbox>
            <el-checkbox label="api" class="permission-checkbox">
              <div class="checkbox-content">
                <span class="checkbox-label">API访问</span>
                <span class="checkbox-desc">调用系统API接口</span>
              </div>
            </el-checkbox>
            <el-checkbox label="export" class="permission-checkbox">
              <div class="checkbox-content">
                <span class="checkbox-label">数据导出</span>
                <span class="checkbox-desc">导出系统数据</span>
              </div>
            </el-checkbox>
          </el-checkbox-group>
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
 * @description 修改卡密的权限配置
 */
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { updateCardPermissions } from '@/api/admin'
import type { Card } from '@/types'

/**
 * Props 定义
 */
interface Props {
  modelValue: boolean           // 弹窗显示状态
  card: Card | null             // 卡密信息
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
const loading = ref(false)                              // 加载状态
const formRef = ref<FormInstance>()                     // 表单引用

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
 * 获取权限列表
 * @param permissions 权限数据（可能是数组或对象）
 * @returns 权限字符串数组
 */
const getPermissions = (permissions: any): string[] => {
  if (Array.isArray(permissions)) {
    return permissions
  }
  if (typeof permissions === 'object' && permissions !== null) {
    return Object.keys(permissions)
  }
  return []
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
    await updateCardPermissions(props.card.id, form.permissions)
    
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
 * 监听卡密变化，初始化权限
 */
watch(() => props.card, (newCard) => {
  if (newCard) {
    form.permissions = getPermissions(newCard.permissions)
  }
}, { immediate: true })

/**
 * 监听弹窗关闭，重置表单
 */
watch(dialogVisible, (newVal) => {
  if (!newVal && formRef.value) {
    setTimeout(() => {
      formRef.value?.resetFields()
    }, 300)
  }
})
</script>

<style scoped>
@reference "../../../styles/index.css";
.permission-dialog {
  @apply py-4;
}

/* 卡密信息 */
.card-info {
  @apply bg-gray-50 rounded-lg p-4 mb-6;
  @apply space-y-2;
}

.info-item {
  @apply flex items-center gap-2;
}

.info-label {
  @apply text-sm font-medium text-gray-600;
}

.info-value {
  @apply text-sm font-mono font-medium text-gray-900;
}

/* 权限表单 */
.permission-form {
  @apply mb-0;
}

.permission-group {
  @apply w-full flex flex-col gap-3;
}

.permission-checkbox {
  @apply w-full;
  @apply bg-white rounded-lg p-4;
  @apply border border-gray-200;
  @apply transition-all duration-200;
}

.permission-checkbox:hover {
  @apply border-blue-300 shadow-sm;
}

.checkbox-content {
  @apply flex flex-col gap-1;
}

.checkbox-label {
  @apply text-sm font-medium text-gray-900;
}

.checkbox-desc {
  @apply text-xs text-gray-500;
}

.dialog-footer {
  @apply flex justify-end gap-3;
}
</style>
