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
          <div class="info-item">
            <span class="info-label">设备限制：</span>
            <el-tag type="info" size="small">
              {{ deviceList.length }} / {{ card.max_device_count }}
            </el-tag>
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
</template>

<script setup lang="ts">
/**
 * 查看设备弹窗组件
 * @description 查看卡密绑定的设备列表
 */
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection, CircleCheck, CircleClose, Refresh } from '@element-plus/icons-vue'
import { getDeviceList, updateDeviceStatus } from '@/api/admin'
import type { Card, Device } from '@/types'

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
 * 加载设备列表
 */
const loadDeviceList = async () => {
  if (!props.card) return
  
  loading.value = true
  try {
    const data = await getDeviceList({
      page: 1,
      size: 100,
      card_id: props.card.id
    })
    deviceList.value = data.devices
  } catch (error) {
    ElMessage.error('加载设备列表失败')
    console.error('加载设备列表失败:', error)
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
 * 监听弹窗打开，加载设备列表
 */
watch(dialogVisible, (newVal) => {
  if (newVal && props.card) {
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

.dialog-footer {
  @apply flex justify-end gap-3;
}
</style>
