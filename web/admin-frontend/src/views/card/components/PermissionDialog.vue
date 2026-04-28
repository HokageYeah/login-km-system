<template>
  <el-dialog
    v-model="dialogVisible"
    width="620px"
    :close-on-click-modal="false"
    :show-close="false"
    class="permission-dialog-root"
    @close="handleClose"
  >
    <!-- 自定义头部 -->
    <template #header>
      <div class="dialog-hero">
        <div class="dialog-hero-bg" />
        <div class="dialog-hero-content">
          <p class="dialog-eyebrow">Permission Config</p>
          <h2 class="dialog-title">修改卡密权限</h2>
          <p class="dialog-desc" v-if="card">
            {{ card.card_key }}
            <el-tag :type="getStatusType(card.status)" size="small" effect="dark" class="ml-2" round>
              {{ getStatusText(card.status) }}
            </el-tag>
          </p>
        </div>
        <el-button
          :icon="Close"
          circle
          class="dialog-close-btn"
          @click="handleClose"
        />
      </div>
    </template>

    <div v-if="card" class="permission-dialog-body">
      <!-- 权限选择 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="permission-form"
      >
        <el-form-item prop="permissions">
          <template #label>
            <div class="form-label-bar">
              <span class="form-label-text">权限配置</span>
              <span class="form-label-count">已选 {{ form.permissions.length }} 项</span>
            </div>
          </template>
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
                        <span class="checkbox-key">{{ permission.permission_key }}</span>
                        <span class="checkbox-name">{{ permission.permission_name }}</span>
                        <span class="checkbox-price" v-if="permission.price">{{ formatPrice(permission.price) }}/月</span>
                        <el-tag v-if="permission.category" size="small" type="info" class="category-tag" round>
                          {{ permission.category }}
                        </el-tag>
                      </div>
                    </div>
                  </el-checkbox>
                </div>
              </template>
              <el-empty v-else description="暂无可用权限" :image-size="80" />
            </el-checkbox-group>
          </div>
        </el-form-item>
      </el-form>

      <!-- 定价面板 -->
      <div class="pricing-panel">
        <div class="pricing-row">
          <span>预计价格</span>
          <strong>{{ formatPrice(pricingBreakdown.finalPrice) }}</strong>
        </div>
        <p>
          权限月价 {{ formatPrice(pricingBreakdown.monthlyPermissionPrice) }}
          ，有效 {{ pricingBreakdown.durationDays }} 天；
          折算 {{ formatPrice(pricingBreakdown.proratedPermissionPrice) }}
          + 设备加价 {{ formatPrice(pricingBreakdown.extraDevicePrice) }}
          = {{ formatPrice(pricingBreakdown.finalPrice) }}。
        </p>
      </div>

      <!-- 提示 -->
      <el-alert
        title="权限修改将立即生效"
        type="warning"
        :closable="false"
        show-icon
        class="mt-4"
      >
        <template #default>
          修改权限后，使用该卡密的用户将立即获得或失去相应权限，卡密价格也会按当前设备数和有效时间重新计算
        </template>
      </el-alert>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" class="footer-btn-cancel">取消</el-button>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleSubmit"
          class="footer-btn-primary"
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
import { Close } from '@element-plus/icons-vue'
import { getCardFeaturePermissions, updateCardFeaturePermissions } from '@/api/feature-permission'
import {
  calculateCardPricingBreakdown,
  formatPrice
} from '@/utils/card-pricing'
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
  success: [card?: Card]
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
const loading = ref(false)
const loadingPermissions = ref(false)
const formRef = ref<FormInstance>()
const availablePermissions = ref<FeaturePermission[]>([])

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

const pricingBreakdown = computed(() => calculateCardPricingBreakdown({
  permissions: form.permissions,
  availablePermissions: availablePermissions.value,
  expireTime: props.card?.expire_time || '',
  maxDeviceCount: props.card?.max_device_count || 1
}))

/**
 * 获取状态标签类型
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
 * 加载卡密权限数据
 */
const loadCardPermissions = async () => {
  if (!props.card) return

  loadingPermissions.value = true
  try {
    const response = await getCardFeaturePermissions(props.card.id)
    availablePermissions.value = response.available_permissions || []

    if (props.permissions && props.permissions.length > 0) {
      form.permissions = [...props.permissions]
    } else {
      form.permissions = response.permission_keys || []
    }
  } catch (error: any) {
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
    await formRef.value.validate()
    loading.value = true

    const result = await updateCardFeaturePermissions(props.card.id, form.permissions)
    const updatedCard: Card = {
      ...props.card,
      permissions: [...form.permissions],
      price: result.price ?? props.card.price
    }

    ElMessage.success('权限修改成功，卡密价格已重新计算')
    emit('success', updatedCard)
    handleClose()
  } catch (error: any) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('修改失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

watch(dialogVisible, (newVal) => {
  if (newVal && props.card) {
    loadCardPermissions()
  }
  if (!newVal && formRef.value) {
    setTimeout(() => {
      formRef.value?.resetFields()
      availablePermissions.value = []
    }, 300)
  }
})
</script>

<style scoped>
@reference "../../../styles/index.css";

/* 弹窗覆写 */
:deep(.permission-dialog-root .el-dialog) {
  @apply rounded-3xl overflow-hidden border-0;
  box-shadow: 0 32px 80px rgba(15, 23, 42, 0.18), 0 0 0 1px rgba(148, 163, 184, 0.1);
}
:deep(.permission-dialog-root .el-dialog__header) { @apply p-0 m-0; }
:deep(.permission-dialog-root .el-dialog__body) { @apply px-6 py-5; }
:deep(.permission-dialog-root .el-dialog__footer) { @apply px-6 pb-5 pt-0; }

/* 头部 Hero */
.dialog-hero {
  @apply relative px-6 pt-6 pb-5 overflow-hidden;
  background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
}
.dialog-hero-bg {
  @apply absolute rounded-full;
  width: 200px; height: 200px; right: -60px; top: -80px;
  background: rgba(255, 255, 255, 0.12);
}
.dialog-hero-content { @apply relative z-10 pr-10; }
.dialog-eyebrow { @apply text-xs font-semibold tracking-[0.18em] uppercase text-blue-100 mb-1.5; }
.dialog-title { @apply text-xl font-bold text-white mb-1; }
.dialog-desc { @apply text-sm text-blue-100 font-mono; }
.dialog-close-btn {
  @apply absolute top-4 right-4 z-20 border-white/30 text-white bg-white/10;
}
.dialog-close-btn:hover { @apply bg-white/20 text-white border-white/50; }

/* 表单 */
.permission-dialog-body { @apply pt-1; }
.permission-form { @apply mb-0; }

.form-label-bar { @apply flex items-center gap-3; }
.form-label-text { @apply text-sm font-semibold text-slate-900; }
.form-label-count { @apply text-xs text-slate-400 font-medium; }

.permission-container {
  @apply w-full min-h-[100px];
}

.permission-group {
  @apply w-full flex flex-col gap-2;
  max-height: 360px;
  overflow-y: auto;
  padding-right: 4px;
}

/* 权限卡片 */
.permission-card {
  @apply w-full rounded-xl border border-slate-200/80 bg-white/60;
  @apply backdrop-blur-sm;
  transition: all 0.15s ease;
  cursor: pointer;
}

.permission-card:hover {
  @apply border-violet-300 bg-violet-50/60;
}

.permission-card-checked {
  @apply border-violet-400 bg-violet-50/80;
  box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.15);
}

.permission-card-checked .checkbox-key,
.permission-card-checked .checkbox-name {
  @apply text-violet-700;
}

.permission-card-disabled {
  @apply opacity-50 cursor-not-allowed bg-slate-50/60;
}
.permission-card-disabled:hover {
  @apply border-slate-200/80 bg-slate-50/60;
}

.permission-checkbox {
  @apply w-full py-3 px-4 m-0;
}
:deep(.el-checkbox__label) { @apply w-full; }
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #8B5CF6;
  border-color: #8B5CF6;
}
:deep(.el-checkbox__input:hover .el-checkbox__inner) {
  border-color: #8B5CF6;
}
:deep(.el-checkbox__inner) {
  @apply w-4 h-4 rounded;
}

/* 复选框内容 */
.checkbox-content { @apply flex flex-col; }
.checkbox-header { @apply flex items-center gap-2 flex-wrap; }
.checkbox-key { @apply text-sm font-semibold text-slate-800; }
.checkbox-name { @apply text-sm text-slate-500; }
.checkbox-price { @apply text-xs font-semibold text-emerald-600 tabular-nums ml-auto; }
.category-tag { @apply text-xs; }

/* 定价面板 */
.pricing-panel {
  @apply mt-3 rounded-2xl border border-violet-100 bg-gradient-to-br from-violet-50/80 to-blue-50/80 p-4;
}
.pricing-row {
  @apply flex items-center justify-between mb-2;
}
.pricing-row span { @apply text-sm text-slate-500; }
.pricing-row strong { @apply text-lg font-bold text-violet-700 tabular-nums; }
.pricing-panel p { @apply text-xs leading-5 text-slate-600; }

/* 滚动条 */
.permission-group::-webkit-scrollbar { @apply w-1.5; }
.permission-group::-webkit-scrollbar-track { @apply bg-transparent; }
.permission-group::-webkit-scrollbar-thumb { @apply bg-slate-200 rounded-full; }
.permission-group::-webkit-scrollbar-thumb:hover { @apply bg-slate-300; }

/* 底部按钮 */
.dialog-footer { @apply flex justify-end gap-3; }
.footer-btn-cancel { @apply rounded-xl; }
.footer-btn-primary {
  @apply rounded-xl border-0 text-white font-medium;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
}
.footer-btn-primary:hover {
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
}

:deep(.el-empty) { @apply py-8; }
</style>
