<template>
  <el-dialog
    v-model="dialogVisible"
    title="查看绑定设备"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="card" class="device-dialog">
      <!-- 卡密信息 -->
      <div class="card-info">
        <div class="info-row">
          <div class="info-item">
            <span class="info-label">卡密：</span>
            <span class="info-value">{{ card.card_key }}</span>
          </div>
          <div class="info-item info-item-limit">
            <span class="info-label">设备限制：</span>
            <el-tag type="info" size="small">
              {{ activeDeviceCount }} / {{ card.max_device_count }}
            </el-tag>
            <el-button
              size="small"
              type="primary"
              plain
              :icon="Edit"
              :loading="maxDeviceCountSubmitting"
              @click="openMaxDeviceCountDialog"
            >
              修改限制
            </el-button>
          </div>
        </div>
      </div>

      <!-- 设备列表 -->
      <el-table
        v-loading="loading"
        :data="deviceList"
        stripe
        class="device-table"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="device_id" label="设备ID" min-width="200">
          <template #default="{ row }">
            <span class="device-id">{{ row.device_id }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="device_name" label="设备名称" min-width="150">
          <template #default="{ row }">
            <span>{{ row.device_name || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="bind_time" label="绑定时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.bind_time) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="last_active_at" label="最后活跃" width="180">
          <template #default="{ row }">
            <div class="active-time-cell">
              <el-icon :class="getActiveClass(row.last_active_at)">
                <Connection />
              </el-icon>
              <span>{{ formatDateTime(row.last_active_at) }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'active' ? 'success' : 'danger'"
              effect="dark"
            >
              {{ row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              :type="row.status === 'disabled' ? 'success' : 'danger'"
              :icon="row.status === 'disabled' ? CircleCheck : CircleClose"
              @click="handleStatusChange(row)"
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
        :image-size="120"
      />
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button
          type="primary"
          :icon="Refresh"
          @click="loadDeviceList"
        >
          刷新
        </el-button>
      </div>
    </template>
  </el-dialog>

  <el-dialog
    v-model="maxDeviceCountDialogVisible"
    title="修改设备限制"
    width="420px"
    :close-on-click-modal="false"
    @closed="resetMaxDeviceCountDialog"
  >
    <div class="limit-dialog-body">
      <p class="limit-dialog-desc">
        当前卡密的最大设备数会直接影响后续新设备绑定校验。
        为保证数据一致性，新的设备上限不能小于当前已绑定设备数。
      </p>

      <div class="limit-summary">
        <div class="limit-summary-item">
          <span class="limit-summary-label">当前卡密</span>
          <span class="limit-summary-value">{{ card?.card_key || '-' }}</span>
        </div>
        <div class="limit-summary-item">
          <span class="limit-summary-label">已绑设备</span>
          <span class="limit-summary-value">{{ activeDeviceCount }}</span>
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
            class="limit-input"
          />
          <div class="form-tip">
            输入范围 1-100，且不能小于当前已绑定设备数 {{ activeDeviceCount }}；保存后会按当前权限和有效时间重新计算卡密价格。
          </div>
          <div class="pricing-panel">
            <div class="pricing-summary">
              <span>预计价格</span>
              <strong>{{ formatPrice(pricingBreakdown.finalPrice) }}</strong>
            </div>
            <p>
              当前：权限月价 {{ formatPrice(pricingBreakdown.monthlyPermissionPrice) }}
              ，有效 {{ pricingBreakdown.durationDays }} 天；
              权限折算后 {{ formatPrice(pricingBreakdown.proratedPermissionPrice) }}
              + 设备加价 {{ formatPrice(pricingBreakdown.extraDevicePrice) }}
              = 最终价格 {{ formatPrice(pricingBreakdown.finalPrice) }}。
            </p>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="maxDeviceCountDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="maxDeviceCountSubmitting"
          @click="handleMaxDeviceCountSubmit"
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
import { Connection, CircleCheck, CircleClose, Refresh, Edit } from '@element-plus/icons-vue'
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
 * @description 这里统一复用当前设备列表中的状态，前端展示和提交校验保持同一口径。
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
 * @param dateStr ISO 8601 格式的日期字符串
 * @returns 格式化后的日期时间字符串
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
 * @param lastActiveAt 最后活跃时间
 * @returns CSS 类名
 */
const getActiveClass = (lastActiveAt: string) => {
  if (!lastActiveAt) return 'inactive-icon'
  
  const lastActive = new Date(lastActiveAt).getTime()
  const now = Date.now()
  const diff = now - lastActive
  
  // 5分钟内活跃
  if (diff < 5 * 60 * 1000) {
    return 'active-icon'
  }
  // 1小时内活跃
  else if (diff < 60 * 60 * 1000) {
    return 'recent-icon'
  }
  // 超过1小时
  else {
    return 'inactive-icon'
  }
}

/**
 * 处理设备状态变更
 * @param device 设备信息
 */
const handleStatusChange = async (device: Device) => {
  const newStatus = device.status === 'disabled' ? 'active' : 'disabled'
  const action = newStatus === 'disabled' ? '禁用' : '启用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}设备 ${device.device_name || device.device_id} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    console.info('[设备弹窗] 开始更新设备状态', {
      cardId: props.card?.id,
      cardKey: props.card?.card_key,
      deviceId: device.id,
      deviceCode: device.device_id,
      oldStatus: device.status,
      newStatus
    })

    await updateDeviceStatus(device.id, newStatus)
    console.info('[设备弹窗] 设备状态更新成功，准备刷新设备列表', {
      cardId: props.card?.id,
      deviceId: device.id,
      newStatus
    })
    ElMessage.success(`${action}成功`)
    loadDeviceList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('[设备弹窗] 设备状态更新失败', {
        cardId: props.card?.id,
        deviceId: device.id,
        targetStatus: newStatus,
        error
      })
      ElMessage.error(`${action}失败`)
    }
  }
}

/**
 * 打开修改最大设备数弹窗
 * @description 将当前卡密的设备上限作为初始值，避免管理员重复输入。
 */
const openMaxDeviceCountDialog = () => {
  if (!props.card) {
    ElMessage.warning('当前卡密信息不存在')
    return
  }

  maxDeviceCountForm.value.max_device_count = props.card.max_device_count
  console.info('[设备弹窗] 打开修改设备限制弹窗', {
    cardId: props.card.id,
    cardKey: props.card.card_key,
    currentMaxDeviceCount: props.card.max_device_count,
    activeDeviceCount: activeDeviceCount.value
  })
  loadPricingPermissions()
  maxDeviceCountDialogVisible.value = true
}

/**
 * 重置修改设备限制弹窗状态
 */
const resetMaxDeviceCountDialog = () => {
  maxDeviceCountSubmitting.value = false
  maxDeviceCountForm.value.max_device_count = props.card?.max_device_count || 1
  console.info('[设备弹窗] 重置修改设备限制弹窗状态', {
    cardId: props.card?.id,
    cardKey: props.card?.card_key,
    resetValue: maxDeviceCountForm.value.max_device_count
  })
}

/**
 * 提交修改最大设备数
 * @description 这里除了基础范围校验外，还会校验不能小于当前活跃设备数，
 * 避免前端先提交一个一定会被后端拒绝的无效请求。
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
    console.info('[设备弹窗] 开始提交新的设备限制', {
      cardId: props.card.id,
      cardKey: props.card.card_key,
      oldMaxDeviceCount: props.card.max_device_count,
      newMaxDeviceCount: targetMaxDeviceCount,
      activeDeviceCount: activeDeviceCount.value
    })

    const result = await updateCardMaxDeviceCount(props.card.id, targetMaxDeviceCount)

    const updatedCard: Card = {
      ...props.card,
      max_device_count: targetMaxDeviceCount,
      price: result.price ?? props.card.price
    }

    console.info('[设备弹窗] 设备限制更新成功', {
      cardId: updatedCard.id,
      cardKey: updatedCard.card_key,
      newMaxDeviceCount: updatedCard.max_device_count,
      newPrice: updatedCard.price
    })

    ElMessage.success('设备限制更新成功，卡密价格已重新计算')
    emit('success', updatedCard)
    maxDeviceCountDialogVisible.value = false
  } catch (error) {
    console.error('[设备弹窗] 设备限制更新失败', {
      cardId: props.card.id,
      cardKey: props.card.card_key,
      targetMaxDeviceCount,
      error
    })
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
    console.info('[设备弹窗] 开始加载设备列表', {
      cardId: props.card.id,
      cardKey: props.card.card_key
    })
    const data = await getDeviceList({
      page: 1,
      size: 100,
      card_id: props.card.id
    })
    deviceList.value = data.devices
    console.info('[设备弹窗] 设备列表加载成功', {
      cardId: props.card.id,
      totalDevices: data.devices.length,
      activeDeviceCount: data.devices.filter(device => device.status === 'active').length
    })
  } catch (error) {
    ElMessage.error('加载设备列表失败')
    console.error('[设备弹窗] 加载设备列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 处理关闭弹窗
 */
const handleClose = () => {
  console.info('[设备弹窗] 关闭设备查看弹窗', {
    cardId: props.card?.id,
    cardKey: props.card?.card_key
  })
  dialogVisible.value = false
}

/**
 * 监听弹窗打开，加载设备列表
 */
watch(dialogVisible, (newVal) => {
  if (newVal && props.card) {
    console.info('[设备弹窗] 弹窗已打开，准备加载数据', {
      cardId: props.card.id,
      cardKey: props.card.card_key,
      maxDeviceCount: props.card.max_device_count
    })
    loadDeviceList()
  }
})
</script>

<style scoped>
@reference "../../../styles/index.css";
.device-dialog {
  @apply py-4;
}

/* 卡密信息 */
.card-info {
  @apply bg-gray-50 rounded-lg p-4 mb-6;
}

.info-row {
  @apply flex items-center gap-6;
}

.info-item {
  @apply flex items-center gap-2;
}

.info-item-limit {
  @apply flex-wrap;
}

.info-label {
  @apply text-sm font-medium text-gray-600;
}

.info-value {
  @apply text-sm font-mono font-medium text-gray-900;
}

/* 设备表格 */
.device-table {
  @apply w-full;
}

.device-id {
  @apply font-mono text-sm text-gray-900;
}

/* 活跃时间单元格 */
.active-time-cell {
  @apply flex items-center gap-2 text-sm;
}

.active-icon {
  @apply text-green-500;
}

.recent-icon {
  @apply text-yellow-500;
}

.inactive-icon {
  @apply text-gray-400;
}

.limit-dialog-body {
  @apply pt-2;
}

.limit-dialog-desc {
  @apply text-sm text-gray-600 leading-6 mb-4;
}

.limit-summary {
  @apply rounded-lg bg-gray-50 border border-gray-200 p-3 mb-4;
}

.limit-summary-item {
  @apply flex items-center justify-between gap-4 text-sm;
}

.limit-summary-item + .limit-summary-item {
  @apply mt-2;
}

.limit-summary-label {
  @apply text-gray-500;
}

.limit-summary-value {
  @apply font-medium text-gray-900 break-all;
}

.limit-input {
  width: 100%;
}

.form-tip {
  @apply text-xs text-gray-500 mt-2 leading-5;
}

.pricing-panel {
  @apply mt-3 rounded-xl border border-blue-100 bg-blue-50 p-4;
  @apply text-xs leading-5 text-blue-900;
}

.pricing-summary {
  @apply flex items-center justify-between mb-2;
}

.pricing-summary span {
  @apply text-gray-500;
}

.pricing-summary strong {
  @apply text-lg font-bold text-blue-700;
  font-variant-numeric: tabular-nums;
}

.dialog-footer {
  @apply flex justify-end gap-3;
}
</style>
