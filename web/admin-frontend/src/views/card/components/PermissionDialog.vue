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

/*
 * 修改权限弹窗（Brutalism 改版）：
 * 弹窗容器外观（黑框 + 硬阴影 + 直角）已由全局主题接管，
 * 这里只处理自定义头部、权限选择卡片与定价面板样式。
 * 复选框勾选态颜色交给全局（墨色），不再本地覆盖紫色。
 */

/* 弹窗容器：只保留排布覆写，圆角/阴影/边框交给全局 */
:deep(.permission-dialog-root .el-dialog__header) { @apply p-0 m-0; }
:deep(.permission-dialog-root .el-dialog__body) { @apply px-6 py-5; }
:deep(.permission-dialog-root .el-dialog__footer) { @apply px-6 pb-5 pt-0; }

/* 头部 Hero：黑底 + 黄色眉题，替代原蓝紫渐变 */
.dialog-hero {
  @apply relative px-6 pt-6 pb-5 overflow-hidden;
  background: var(--ink);
}

/* 右上角黄色几何块：平面色块装饰，无模糊无渐变 */
.dialog-hero-bg {
  @apply absolute;
  width: 140px;
  height: 140px;
  right: -46px;
  top: -56px;
  background: var(--accent);
  transform: rotate(14deg);
}

.dialog-hero-content { @apply relative z-10 pr-10; }

.dialog-eyebrow {
  @apply text-xs tracking-[0.18em] uppercase mb-1.5;
  font-weight: 800;
  color: var(--accent);
}

.dialog-title {
  @apply text-xl mb-1;
  font-weight: 900;
  color: var(--surface);
}

.dialog-desc {
  @apply text-sm font-mono;
  color: var(--paper);
}

/* 关闭按钮：黄色方块（直角），在黑底上形成强对比 */
.dialog-close-btn {
  border-radius: 0;
  background: var(--accent);
  border-color: var(--accent);
  color: var(--ink);
}

.dialog-close-btn:hover {
  background: var(--accent-soft);
  border-color: var(--accent-soft);
  color: var(--ink);
  transform: translate(-1px, -1px);
  box-shadow: 3px 3px 0 var(--accent);
}

/* 表单 */
.permission-dialog-body { @apply pt-1; }
.permission-form { @apply mb-0; }

.form-label-bar { @apply flex items-center gap-3; }

.form-label-text {
  @apply text-sm;
  font-weight: 800;
  color: var(--ink);
}

.form-label-count {
  @apply text-xs;
  font-weight: 700;
  color: var(--ink-soft);
}

.permission-container {
  @apply w-full min-h-[100px];
}

.permission-group {
  @apply w-full flex flex-col gap-2;
  max-height: 360px;
  overflow-y: auto;
  padding-right: 4px;
}

/* 权限卡片：白底 + 柔和边框，hover 提边框 */
.permission-card {
  @apply w-full;
  background: var(--surface);
  border: 2px solid var(--line-soft);
  transition: all 0.15s ease;
  cursor: pointer;
}

.permission-card:hover {
  border-color: var(--ink);
}

/* 选中态：黄色高亮 + 黑框 + 硬阴影，一眼区分已选权限 */
.permission-card-checked {
  background: var(--accent-soft);
  border: 2px solid var(--ink);
  box-shadow: var(--shadow-brutal-sm);
}

.permission-card-checked .checkbox-key,
.permission-card-checked .checkbox-name {
  color: var(--ink);
}

.permission-card-disabled {
  @apply opacity-50 cursor-not-allowed;
  background: var(--paper);
}

.permission-card-disabled:hover {
  border-color: var(--line-soft);
}

.permission-checkbox {
  @apply w-full py-3 px-4 m-0;
}

:deep(.el-checkbox__label) { @apply w-full; }

/* 勾选态颜色交给全局（墨色方块），这里只保留尺寸 */
:deep(.el-checkbox__inner) {
  @apply w-4 h-4;
}

/* 复选框内容 */
.checkbox-content { @apply flex flex-col; }
.checkbox-header { @apply flex items-center gap-2 flex-wrap; }

.checkbox-key {
  @apply text-sm;
  font-weight: 700;
  color: var(--ink);
}

.checkbox-name {
  @apply text-sm;
  color: var(--ink-soft);
  font-weight: 600;
}

/* 价格用 success 语义色：金额是正向经营信息 */
.checkbox-price {
  @apply text-xs tabular-nums ml-auto;
  font-weight: 800;
  color: #1a7f37;
}

.category-tag { @apply text-xs; }

/* 定价面板：黄色弱化底 + 黑框，金额是弹窗内的关键决策信息 */
.pricing-panel {
  @apply mt-3 p-4;
  background: var(--accent-soft);
  border: 2px solid var(--ink);
}

.pricing-row {
  @apply flex items-center justify-between mb-2;
}

.pricing-row span {
  @apply text-sm;
  color: var(--ink-soft);
  font-weight: 600;
}

.pricing-row strong {
  @apply text-lg tabular-nums;
  font-weight: 900;
  color: var(--ink);
}

.pricing-panel p {
  @apply text-xs leading-5;
  color: var(--ink-soft);
}

/* 滚动条：方块拇指，贴合直角语言 */
.permission-group::-webkit-scrollbar { @apply w-1.5; }
.permission-group::-webkit-scrollbar-track { @apply bg-transparent; }
.permission-group::-webkit-scrollbar-thumb { background: var(--line-soft); }
.permission-group::-webkit-scrollbar-thumb:hover { background: var(--ink-soft); }

/* 底部按钮：外观交给全局主题 */
.dialog-footer { @apply flex justify-end gap-3; }

:deep(.el-empty) { @apply py-8; }
</style>
