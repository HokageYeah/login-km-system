<template>
  <div class="device-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">设备管理</h1>
        <p class="page-subtitle">监控与管理系统中的所有绑定设备</p>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="卡密ID">
          <el-input
            v-model.number="filterForm.card_id"
            placeholder="输入卡密ID"
            clearable
            class="filter-input"
            type="number"
          />
        </el-form-item>
        
        <el-form-item label="用户ID">
          <el-input
            v-model.number="filterForm.user_id"
            placeholder="输入用户ID"
            clearable
            class="filter-input"
            type="number"
          />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="选择状态"
            clearable
            class="filter-select"
          >
            <el-option label="激活" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 设备列表表格 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="deviceList"
        stripe
        class="device-table"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="device_id" label="设备ID" min-width="200">
          <template #default="{ row }">
            <div class="device-id-cell">
              <el-icon class="device-icon"><Monitor /></el-icon>
              <span class="device-id-text">{{ row.device_id }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="device_name" label="设备名称" min-width="150">
          <template #default="{ row }">
            <span>{{ row.device_name || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="card_key" label="关联卡密" min-width="200">
          <template #default="{ row }">
            <div class="card-key-cell">
              <span class="card-key-text">{{ row.card_key }}</span>
              <el-button
                :icon="CopyDocument"
                size="small"
                text
                @click="copyCardKey(row.card_key)"
                class="copy-btn"
              />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="username" label="关联用户" width="120">
          <template #default="{ row }">
            <span>{{ row.username || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="bind_time" label="绑定时间" width="180">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Clock /></el-icon>
              <span>{{ formatDateTime(row.bind_time) }}</span>
            </div>
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
              class="status-tag"
            >
              {{ row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
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

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 设备管理页面
 * @description 管理员管理系统中的所有绑定设备
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Monitor,
  Clock,
  Connection,
  CopyDocument,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'
import { getDeviceList, updateDeviceStatus } from '@/api/admin'
import type { Device } from '@/types'

/**
 * 状态定义
 */
const loading = ref(false)                              // 加载状态
const deviceList = ref<Device[]>([])                    // 设备列表

/**
 * 筛选表单
 */
const filterForm = reactive({
  card_id: undefined as number | undefined,
  user_id: undefined as number | undefined,
  status: ''
})

/**
 * 分页参数
 */
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

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
 * 复制卡密
 * @param cardKey 卡密字符串
 */
const copyCardKey = async (cardKey: string) => {
  try {
    await navigator.clipboard.writeText(cardKey)
    ElMessage.success('卡密已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

/**
 * 处理状态变更
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
        type: 'warning',
        dangerouslyUseHTMLString: true,
        message: `
          <div>
            <p>设备ID：<strong>${device.device_id}</strong></p>
            <p>设备名称：<strong>${device.device_name || '未命名'}</strong></p>
            <p>关联卡密：<strong>${device.card_key}</strong></p>
            <p style="color: #f56c6c; margin-top: 10px;">
              ${newStatus === 'disabled' ? '禁用后该设备将无法使用卡密功能' : '启用后该设备将恢复正常使用'}
            </p>
          </div>
        `
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
 * 处理搜索
 */
const handleSearch = () => {
  pagination.page = 1
  loadDeviceList()
}

/**
 * 处理重置
 */
const handleReset = () => {
  filterForm.card_id = undefined
  filterForm.user_id = undefined
  filterForm.status = ''
  pagination.page = 1
  loadDeviceList()
}

/**
 * 处理页码变化
 */
const handlePageChange = (page: number) => {
  pagination.page = page
  loadDeviceList()
}

/**
 * 处理每页数量变化
 */
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadDeviceList()
}

/**
 * 加载设备列表
 */
const loadDeviceList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    
    if (filterForm.card_id) {
      params.card_id = filterForm.card_id
    }
    if (filterForm.user_id) {
      params.user_id = filterForm.user_id
    }
    if (filterForm.status) {
      params.status = filterForm.status
    }
    
    const data = await getDeviceList(params)
    deviceList.value = data.devices
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('加载设备列表失败')
    console.error('加载设备列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadDeviceList()
})
</script>

<style scoped>
@reference "../../styles/index.css";
.device-management-container {
  @apply w-full h-full p-8;
  @apply bg-gradient-to-br from-gray-50 to-gray-100;
  min-height: calc(100vh - 64px);
}

/* 页面头部 */
.page-header {
  @apply flex justify-between items-center mb-8;
}

.page-title {
  @apply text-3xl font-bold text-gray-900 mb-2;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  @apply text-base text-gray-600;
}

/* 筛选区域 */
.filter-section {
  @apply bg-white rounded-2xl p-6 mb-6;
  @apply shadow-sm border border-gray-100;
}

.filter-form {
  @apply mb-0;
}

.filter-select {
  @apply w-48;
}

.filter-input {
  @apply w-48;
}

/* 表格区域 */
.table-section {
  @apply bg-white rounded-2xl p-6;
  @apply shadow-sm border border-gray-100;
}

.device-table {
  @apply w-full;
}

/* 设备ID单元格 */
.device-id-cell {
  @apply flex items-center gap-2;
}

.device-icon {
  @apply text-blue-600;
}

.device-id-text {
  @apply font-mono text-sm font-medium text-gray-900;
}

/* 卡密单元格 */
.card-key-cell {
  @apply flex items-center gap-2;
}

.card-key-text {
  @apply font-mono text-sm font-medium text-gray-900;
}

.copy-btn {
  @apply text-blue-600;
}

/* 状态标签 */
.status-tag {
  @apply font-medium;
}

/* 时间单元格 */
.time-cell {
  @apply flex items-center gap-2 text-sm text-gray-600;
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

/* 分页 */
.pagination-section {
  @apply flex justify-end mt-6;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .page-header {
    @apply flex-col gap-4;
  }

  .filter-form {
    @apply flex-col;
  }

  .filter-select,
  .filter-input {
    @apply w-full;
  }
}
</style>
