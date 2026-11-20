<template>
  <el-dialog
    v-model="dialogVisible"
    width="920px"
    :close-on-click-modal="false"
    :show-close="false"
    class="device-dialog-root"
    @close="handleClose"
  >
    <!-- 自定义头部 -->
    <template #header>
      <div class="dialog-hero">
        <div class="dialog-hero-bg" />
        <div class="dialog-hero-content">
          <p class="dialog-eyebrow">Device Bindings</p>
          <h2 class="dialog-title">查看绑定设备</h2>
          <p class="dialog-desc" v-if="card">
            {{ card.card_key }} · 已绑定 {{ activeDeviceCount }} / {{ card.max_device_count }} 台
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

    <div v-if="card" class="device-dialog-body">
      <!-- 卡密摘要 -->
      <div class="card-summary">
        <div class="summary-item">
          <span class="summary-label">卡密</span>
          <strong class="summary-value mono-text">{{ card.card_key }}</strong>
        </div>
        <div class="summary-item">
          <span class="summary-label">设备限制</span>
          <strong class="summary-value">{{ activeDeviceCount }} / {{ card.max_device_count }}</strong>
        </div>
        <div class="summary-item">
          <el-button
            size="small"
            type="primary"
            plain
            :icon="Edit"
            :loading="maxDeviceCountSubmitting"
            @click="openMaxDeviceCountDialog"
            class="summary-action-btn"
          >
            修改限制
          </el-button>
        </div>
      </div>

      <!-- 设备列表 -->
      <el-table
        v-loading="loading"
        :data="deviceList"
        class="device-table"
      >
        <el-table-column prop="id" label="ID" width="70" />

        <el-table-column prop="device_id" label="设备ID" min-width="200">
          <template #default="{ row }">
            <span class="device-id">{{ row.device_id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="device_name" label="设备名称" min-width="140">
          <template #default="{ row }">
            <span>{{ row.device_name || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="bind_time" label="绑定时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.bind_time) }}
          </template>
        </el-table-column>

        <el-table-column prop="last_active_at" label="最后活跃" width="170">
          <template #default="{ row }">
            <div class="active-time-cell">
              <span class="active-dot" :class="getActiveClass(row.last_active_at)" />
              <span>{{ formatDateTime(row.last_active_at) }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'active' ? 'success' : 'danger'"
              effect="dark"
              size="small"
              round
            >
              {{ row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              size="small"
              :type="row.status === 'disabled' ? 'success' : 'danger'"
              :icon="row.status === 'disabled' ? CircleCheck : CircleClose"
              @click="handleStatusChange(row)"
              class="action-btn"
            >
              {{ row.status === 'disabled' ? '启用' : '禁用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-if="!loading && deviceList.length === 0"
        description="暂无绑定设备"
        :image-size="100"
      />
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" class="footer-btn-cancel">关闭</el-button>
        <el-button
          type="primary"
          :icon="Refresh"
          @click="loadDeviceList"
          class="footer-btn-primary"
        >
          刷新
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 修改设备限制子弹窗 -->
  <el-dialog
    v-model="maxDeviceCountDialogVisible"
    width="460px"
    :close-on-click-modal="false"
    :show-close="false"
    class="device-limit-dialog-root"
    @closed="resetMaxDeviceCountDialog"
  >
    <template #header>
      <div class="sub-dialog-header">
        <h3 class="sub-dialog-title">修改设备限制</h3>
        <el-button
          :icon="Close"
          circle
          class="sub-dialog-close-btn"
          @click="maxDeviceCountDialogVisible = false"
        />
      </div>
    </template>

    <div class="limit-dialog-body">
      <p class="limit-dialog-desc">
        新的设备上限不能小于当前已绑定设备数，保存后会重新计算卡密价格。
      </p>

      <div class="limit-summary">
        <div class="limit-summary-item">
          <span>当前卡密</span>
          <strong class="mono-text">{{ card?.card_key || '-' }}</strong>
        </div>
        <div class="limit-summary-item">
          <span>已绑设备</span>
          <strong>{{ activeDeviceCount }} 台</strong>
        </div>
      </div>

      <el-form label-position="top">
        <el-form-item label="最大设备数">
          <el-input-number
            v-model="maxDeviceCountForm.max_device_count"
            :min="Math.max(activeDeviceCount, 1)"
            :max="100"
            :step="1"
            controls-position="right"
            class="w-full"
          />
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
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="maxDeviceCountDialogVisible = false" class="footer-btn-cancel">取消</el-button>
        <el-button
          type="primary"
          :loading="maxDeviceCountSubmitting"
          @click="handleMaxDeviceCountSubmit"
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
 * 查看设备弹窗组件
 * @description 查看卡密绑定的设备列表
 */
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection, CircleCheck, CircleClose, Close, Refresh, Edit } from '@element-plus/icons-vue'
import { getDeviceList, updateCardMaxDeviceCount, updateDeviceStatus } from '@/api/admin'
import { getFeaturePermissionList } from '@/api/feature-permission'
import {
  calculateCardPricingBreakdown,
  formatPrice
} from '@/utils/card-pricing'
import type { Card, Device, FeaturePermission } from '@/types'

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
const loading = ref(false)                              // 加载状态
const deviceList = ref<Device[]>([])                    // 设备列表
const availablePermissions = ref<FeaturePermission[]>([]) // 当前应用可用权限，用于价格拆解展示
const maxDeviceCountDialogVisible = ref(false)          // 修改设备限制弹窗显示状态
const maxDeviceCountSubmitting = ref(false)             // 修改设备限制提交状态
const maxDeviceCountForm = ref({
  max_device_count: 1
})

/**
 * 当前活跃设备数量
 */
const activeDeviceCount = computed(() => {
  return deviceList.value.filter(device => device.status === 'active').length
})

const pricingBreakdown = computed(() => calculateCardPricingBreakdown({
  permissions: props.card?.permissions || [],
  availablePermissions: availablePermissions.value,
  expireTime: props.card?.expire_time || '',
  maxDeviceCount: maxDeviceCountForm.value.max_device_count
}))

const loadPricingPermissions = async () => {
  if (!props.card?.app_id) {
    availablePermissions.value = []
    return
  }

  try {
    const response = await getFeaturePermissionList({
      page: 1,
      size: 100,
      app_id: props.card.app_id
    })
    availablePermissions.value = response.permissions || []
  } catch (error) {
    console.error('[设备弹窗] 加载价格计算所需权限失败', error)
    availablePermissions.value = []
  }
}

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
 * 获取活跃状态样式类
 */
const getActiveClass = (lastActiveAt: string) => {
  if (!lastActiveAt) return 'dot-inactive'
  const diff = Date.now() - new Date(lastActiveAt).getTime()
  if (diff < 5 * 60 * 1000) return 'dot-active'
  if (diff < 60 * 60 * 1000) return 'dot-recent'
  return 'dot-inactive'
}

/**
 * 处理设备状态变更
 */
const handleStatusChange = async (device: Device) => {
  const newStatus = device.status === 'disabled' ? 'active' : 'disabled'
  const action = newStatus === 'disabled' ? '禁用' : '启用'

  try {
    await ElMessageBox.confirm(
      `确定要${action}设备 ${device.device_name || device.device_id} 吗？`,
      '确认操作',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )

    await updateDeviceStatus(device.id, newStatus)
    ElMessage.success(`${action}成功`)
    loadDeviceList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`${action}失败`)
    }
  }
}

/**
 * 打开修改最大设备数弹窗
 */
const openMaxDeviceCountDialog = () => {
  if (!props.card) {
    ElMessage.warning('当前卡密信息不存在')
    return
  }
  maxDeviceCountForm.value.max_device_count = props.card.max_device_count
  loadPricingPermissions()
  maxDeviceCountDialogVisible.value = true
}

/**
 * 重置修改设备限制弹窗状态
 */
const resetMaxDeviceCountDialog = () => {
  maxDeviceCountSubmitting.value = false
  maxDeviceCountForm.value.max_device_count = props.card?.max_device_count || 1
}

/**
 * 提交修改最大设备数
 */
const handleMaxDeviceCountSubmit = async () => {
  if (!props.card) {
    ElMessage.warning('当前卡密信息不存在')
    return
  }

  const targetMaxDeviceCount = Number(maxDeviceCountForm.value.max_device_count)
  if (!Number.isInteger(targetMaxDeviceCount) || targetMaxDeviceCount < 1 || targetMaxDeviceCount > 100) {
    ElMessage.warning('最大设备数范围必须在 1-100 之间')
    return
  }

  if (targetMaxDeviceCount < activeDeviceCount.value) {
    ElMessage.warning(`新的设备上限不能小于当前已绑定设备数（${activeDeviceCount.value}台）`)
    return
  }

  maxDeviceCountSubmitting.value = true
  try {
    const result = await updateCardMaxDeviceCount(props.card.id, targetMaxDeviceCount)
    const updatedCard: Card = {
      ...props.card,
      max_device_count: targetMaxDeviceCount,
      price: result.price ?? props.card.price
    }
    ElMessage.success('设备限制更新成功，卡密价格已重新计算')
    emit('success', updatedCard)
    maxDeviceCountDialogVisible.value = false
  } catch (error) {
    ElMessage.error('设备限制更新失败')
  } finally {
    maxDeviceCountSubmitting.value = false
  }
}

/**
 * 加载设备列表
 */
const loadDeviceList = async () => {
  if (!props.card) return
  loading.value = true
  try {
    const data = await getDeviceList({ page: 1, size: 100, card_id: props.card.id })
    deviceList.value = data.devices
  } catch (error) {
    ElMessage.error('加载设备列表失败')
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

watch(dialogVisible, (newVal) => {
  if (newVal && props.card) {
    loadDeviceList()
  }
})
</script>

<style scoped>
@reference "../../../styles/index.css";

/*
 * 查看设备弹窗（Brutalism 改版）：
 * 弹窗容器外观（黑框 + 硬阴影 + 直角）已由全局主题接管，
 * 这里只覆写自定义头部的排布与内部摘要/定价等业务块样式。
 * 头部 Hero 改为黑底 + 黄色眉题，替代原蓝紫渐变与白色光斑。
 */

/* 主弹窗：仅保留结构性内边距覆写，去掉与全局冲突的圆角与弥散阴影 */
:deep(.device-dialog-root .el-dialog__header) { @apply p-0 m-0; }
:deep(.device-dialog-root .el-dialog__body) { @apply px-6 py-5; }
:deep(.device-dialog-root .el-dialog__footer) { @apply px-6 pb-5 pt-0; }

/* 子弹窗：同上 */
:deep(.device-limit-dialog-root .el-dialog__header) { @apply p-0 m-0; }
:deep(.device-limit-dialog-root .el-dialog__body) { @apply px-6 py-5; }
:deep(.device-limit-dialog-root .el-dialog__footer) { @apply px-6 pb-5 pt-0; }

/* 头部 Hero：黑底 + 黄色眉题 */
.dialog-hero {
  @apply relative px-6 pt-6 pb-5 overflow-hidden;
  background: var(--ink);
}

/* 右上角黄色几何块：平面色块装饰（无模糊、无渐变），overflow-hidden 裁切 */
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

/* 子弹窗头部：黑色粗分隔线，与全局对话框标题栏语言一致 */
.sub-dialog-header {
  @apply flex items-center justify-between px-6 py-4;
  border-bottom: 2px solid var(--ink);
}

.sub-dialog-title {
  @apply text-base;
  font-weight: 900;
  color: var(--ink);
}

/* circle 属性只影响默认圆角，这里强制直角 */
.sub-dialog-close-btn {
  border-radius: 0;
}

/* 卡密摘要条：纸色底 + 柔和边框（面板内的次级信息块） */
.card-summary {
  @apply flex items-center gap-4 flex-wrap mb-5 p-4;
  background: var(--paper);
  border: 2px solid var(--line-soft);
}

.summary-item { @apply flex items-center gap-2; }

.summary-label {
  @apply text-xs;
  font-weight: 700;
  color: var(--ink-soft);
}

.summary-value {
  @apply text-sm;
  font-weight: 800;
  color: var(--ink);
}

/* 设备表格 */
.device-table { @apply w-full; }

.device-id {
  @apply font-mono text-sm;
  font-weight: 600;
  color: var(--ink);
}

/* 活跃状态：方块指示灯（黑框直角），去掉圆形与辉光 */
.active-time-cell {
  @apply flex items-center gap-2 text-sm;
  color: var(--ink-soft);
  font-weight: 600;
}

.active-dot {
  @apply w-2.5 h-2.5 shrink-0;
  border: 2px solid var(--ink);
}

.dot-active { background: #1a7f37; }
.dot-recent { background: #e8a13a; }
.dot-inactive { background: var(--line-soft); }

/* 修改限制子弹窗 */
.limit-dialog-body { @apply pt-2; }

.limit-dialog-desc {
  @apply text-sm leading-6 mb-4;
  color: var(--ink-soft);
  font-weight: 600;
}

.limit-summary {
  @apply grid grid-cols-2 gap-3 mb-4;
}

.limit-summary-item {
  @apply p-3;
  background: var(--paper);
  border: 2px solid var(--line-soft);
}

.limit-summary-item span {
  @apply block text-xs mb-1;
  color: var(--ink-soft);
  font-weight: 700;
}

.limit-summary-item strong {
  @apply text-sm;
  font-weight: 800;
  color: var(--ink);
}

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

/* 底部按钮：外观交给全局（default / primary 黑框体系） */
.dialog-footer { @apply flex justify-end gap-3; }

.mono-text { @apply font-mono; }
</style>
