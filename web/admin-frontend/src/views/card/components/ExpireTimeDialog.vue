<template>
  <el-dialog
    v-model="dialogVisible"
    width="480px"
    :close-on-click-modal="false"
    :show-close="false"
    class="expire-dialog-root"
    @close="handleClose"
  >
    <!-- 自定义头部 -->
    <template #header>
      <div class="dialog-hero">
        <div class="dialog-hero-bg" />
        <div class="dialog-hero-content">
          <p class="dialog-eyebrow">Expiration Time</p>
          <h2 class="dialog-title">修改过期时间</h2>
          <p class="dialog-desc" v-if="card">
            {{ card.card_key }}
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

    <div v-if="card" class="expire-dialog-body">
      <!-- 当前过期时间预览 -->
      <div class="current-preview">
        <div class="preview-item">
          <span>当前过期时间</span>
          <strong>{{ formatDateTime(card.expire_time) }}</strong>
        </div>
      </div>

      <!-- 新过期时间选择 -->
      <el-form label-position="top">
        <el-form-item label="新的过期时间" required>
          <el-date-picker
            v-model="expireTimeForm.expire_time"
            type="datetime"
            placeholder="请选择新的过期时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
            class="w-full"
          />
          <div class="shortcut-panel">
            <span class="shortcut-panel-label">快捷选择</span>
            <div class="shortcut-chips">
              <button
                v-for="shortcut in expireShortcutOptions"
                :key="shortcut.key"
                type="button"
                class="shortcut-chip"
                @click="handleShortcutSelect(shortcut.key)"
              >
                {{ shortcut.label }}
              </button>
            </div>
          </div>
          <div class="form-tip">
            可选择未来时间延长有效期，也可选择过去时间让卡密立即进入已过期状态；保存后会按当前设备数和权限重新计算卡密价格。
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
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" class="footer-btn-cancel">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
          class="footer-btn-primary"
        >
          保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
/**
 * 修改过期时间弹窗组件
 * @description 修改卡密过期时间，自动重新计算价格
 */
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import { updateCardExpireTime } from '@/api/admin'
import { getFeaturePermissionList } from '@/api/feature-permission'
import {
  EXPIRE_SHORTCUT_OPTIONS,
  formatDateTimeValue,
  getExpireShortcutValue,
  type ExpireShortcutKey
} from '@/utils/expire-shortcuts'
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
}

const props = defineProps<Props>()

/**
 * Emits 定义
 */
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: [card: Card]
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
const submitting = ref(false)
const expireShortcutOptions = EXPIRE_SHORTCUT_OPTIONS
const pricingPermissions = ref<FeaturePermission[]>([])

const expireTimeForm = reactive({
  expire_time: ''
})

const pricingBreakdown = computed(() => calculateCardPricingBreakdown({
  permissions: props.card?.permissions || [],
  availablePermissions: pricingPermissions.value,
  expireTime: expireTimeForm.expire_time,
  maxDeviceCount: props.card?.max_device_count || 1
}))

/**
 * 格式化日期时间
 */
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 加载价格计算所需权限
 */
const loadPricingPermissions = async () => {
  if (!props.card?.app_id) {
    pricingPermissions.value = []
    return
  }
  try {
    const response = await getFeaturePermissionList({
      page: 1,
      size: 100,
      app_id: props.card.app_id
    })
    pricingPermissions.value = response.permissions || []
  } catch (error) {
    console.error('[修改过期时间弹窗] 加载权限失败', error)
    pricingPermissions.value = []
  }
}

/**
 * 处理快捷时间选择
 */
const handleShortcutSelect = (shortcutKey: ExpireShortcutKey) => {
  expireTimeForm.expire_time = getExpireShortcutValue(shortcutKey)
}

/**
 * 提交修改
 */
const handleSubmit = async () => {
  if (!props.card) {
    ElMessage.warning('当前卡密信息不存在')
    return
  }
  if (!expireTimeForm.expire_time) {
    ElMessage.warning('请选择新的过期时间')
    return
  }

  submitting.value = true
  try {
    const result = await updateCardExpireTime(props.card.id, expireTimeForm.expire_time)

    const isExpired = expireTimeForm.expire_time
      ? new Date(expireTimeForm.expire_time).getTime() < Date.now()
      : false

    const updatedCard: Card = {
      ...props.card,
      expire_time: expireTimeForm.expire_time,
      is_expired: isExpired,
      price: result.price ?? props.card.price
    }

    ElMessage.success('卡密过期时间更新成功，卡密价格已重新计算')
    emit('success', updatedCard)
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('卡密过期时间更新失败')
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

/**
 * 监听弹窗打开，初始化数据
 */
watch(dialogVisible, (newVal) => {
  if (newVal && props.card) {
    expireTimeForm.expire_time = formatDateTimeValue(new Date())
    loadPricingPermissions()
  } else if (!newVal) {
    setTimeout(() => {
      expireTimeForm.expire_time = ''
      pricingPermissions.value = []
      submitting.value = false
    }, 300)
  }
})
</script>

<style scoped>
@reference "../../../styles/index.css";

/* 弹窗覆写 */
:deep(.expire-dialog-root .el-dialog) {
  @apply rounded-3xl overflow-hidden border-0;
  box-shadow: 0 32px 80px rgba(15, 23, 42, 0.18), 0 0 0 1px rgba(148, 163, 184, 0.1);
}
:deep(.expire-dialog-root .el-dialog__header) { @apply p-0 m-0; }
:deep(.expire-dialog-root .el-dialog__body) { @apply px-6 py-5; }
:deep(.expire-dialog-root .el-dialog__footer) { @apply px-6 pb-5 pt-0; }

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

/* 弹窗主体 */
.expire-dialog-body { @apply pt-1; }

/* 当前过期时间预览 */
.current-preview {
  @apply rounded-2xl border border-slate-200/80 bg-white/60 p-4 mb-5;
  @apply backdrop-blur-sm;
}
.preview-item {
  @apply flex items-center justify-between;
}
.preview-item span { @apply text-xs text-slate-400 font-medium; }
.preview-item strong { @apply text-sm text-slate-900 font-semibold; }

/* 快捷选择面板 */
.shortcut-panel {
  @apply mt-3 w-full rounded-2xl border border-slate-200/80 bg-slate-50/60 p-3;
}
.shortcut-panel-label {
  @apply block text-xs text-slate-400 font-medium mb-2;
}
.shortcut-chips {
  @apply flex flex-wrap gap-1.5;
}
.shortcut-chip {
  @apply text-xs px-3 py-1.5 rounded-lg cursor-pointer font-medium;
  @apply border border-slate-200 bg-white text-slate-600;
  transition: all 0.15s ease;
}
.shortcut-chip:hover {
  @apply border-violet-300 bg-violet-50 text-violet-700;
}

.form-tip {
  @apply mt-2 text-xs text-slate-400 leading-5;
}

/* 定价面板 */
.pricing-panel {
  @apply mt-4 rounded-2xl border border-violet-100 bg-gradient-to-br from-violet-50/80 to-blue-50/80 p-4;
}
.pricing-row {
  @apply flex items-center justify-between mb-2;
}
.pricing-row span { @apply text-sm text-slate-500; }
.pricing-row strong { @apply text-lg font-bold text-violet-700 tabular-nums; }
.pricing-panel p { @apply text-xs leading-5 text-slate-600; }

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
</style>
