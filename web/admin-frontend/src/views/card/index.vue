<template>
  <div class="card-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">卡密管理</h1>
        <p class="page-subtitle">管理系统中的所有卡密，支持生成、查询、状态管理</p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          :icon="Plus"
          @click="showGenerateDialog"
          class="generate-btn"
        >
          生成卡密
        </el-button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="应用">
          <el-select
            v-model="filterForm.app_id"
            placeholder="选择应用"
            clearable
            class="filter-select"
          >
            <el-option
              v-for="app in appList"
              :key="app.id"
              :label="app.app_name"
              :value="app.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="选择状态"
            clearable
            class="filter-select"
          >
            <el-option label="未使用" value="unused" />
            <el-option label="已使用" value="used" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索卡密或备注"
            clearable
            class="filter-input"
            :prefix-icon="Search"
          />
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

    <!-- 卡密列表表格 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="cardList"
        stripe
        class="card-table"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="id" label="ID" width="80" sortable="custom" />
        
        <el-table-column prop="card_key" label="卡密" min-width="200">
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
        
        <el-table-column prop="app_name" label="所属应用" width="120" />
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.status)"
              effect="dark"
              class="status-tag"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="expire_time" label="过期时间" width="180">
          <template #default="{ row }">
            <div class="expire-time-cell">
              <el-icon><Clock /></el-icon>
              <span>{{ formatDateTime(row.expire_time) }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="max_device_count" label="设备限制" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">
              {{ row.bind_device_count || 0 }} / {{ row.max_device_count }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="permissions" label="权限" min-width="150">
          <template #default="{ row }">
            <div class="permissions-cell">
              <el-tag
                v-for="(perm, index) in getPermissions(row.permissions)"
                :key="index"
                size="small"
                class="permission-tag"
              >
                {{ perm }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                size="small"
                :icon="View"
                @click="showDeviceDialog(row)"
              >
                查看设备
              </el-button>
              <el-button
                size="small"
                :icon="Edit"
                @click="showPermissionDialog(row)"
              >
                修改权限
              </el-button>
              <el-button
                size="small"
                :type="row.status === 'disabled' ? 'success' : 'danger'"
                :icon="row.status === 'disabled' ? CircleCheck : CircleClose"
                @click="handleStatusChange(row)"
              >
                {{ row.status === 'disabled' ? '启用' : '禁用' }}
              </el-button>
            </div>
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

    <!-- 生成卡密弹窗 -->
    <GenerateDialog
      v-model="generateDialogVisible"
      :app-list="appList"
      @success="handleGenerateSuccess"
    />

    <!-- 修改权限弹窗 -->
    <PermissionDialog
      v-model="permissionDialogVisible"
      :card="currentCard"
      @success="handlePermissionSuccess"
    />

    <!-- 查看设备弹窗 -->
    <DeviceDialog
      v-model="deviceDialogVisible"
      :card="currentCard"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 卡密管理页面
 * @description 管理员管理系统中的所有卡密
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  CopyDocument,
  Clock,
  View,
  Edit,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'
import { getCardList, updateCardStatus } from '@/api/admin'
import { getAppList } from '@/api/app'
import type { Card, App } from '@/types'
import GenerateDialog from './components/GenerateDialog.vue'
import PermissionDialog from './components/PermissionDialog.vue'
import DeviceDialog from './components/DeviceDialog.vue'

/**
 * 状态定义
 */
const loading = ref(false)                              // 加载状态
const cardList = ref<Card[]>([])                        // 卡密列表
const appList = ref<App[]>([])                          // 应用列表
const currentCard = ref<Card | null>(null)              // 当前操作的卡密

/**
 * 弹窗显示状态
 */
const generateDialogVisible = ref(false)                // 生成卡密弹窗
const permissionDialogVisible = ref(false)              // 修改权限弹窗
const deviceDialogVisible = ref(false)                  // 查看设备弹窗

/**
 * 筛选表单
 */
const filterForm = reactive({
  app_id: undefined as number | undefined,
  status: '',
  keyword: ''
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
 * 显示生成卡密弹窗
 */
const showGenerateDialog = () => {
  generateDialogVisible.value = true
}

/**
 * 显示修改权限弹窗
 * @param card 卡密信息
 */
const showPermissionDialog = (card: Card) => {
  currentCard.value = card
  permissionDialogVisible.value = true
}

/**
 * 显示查看设备弹窗
 * @param card 卡密信息
 */
const showDeviceDialog = (card: Card) => {
  currentCard.value = card
  deviceDialogVisible.value = true
}

/**
 * 处理状态变更
 * @param card 卡密信息
 */
const handleStatusChange = async (card: Card) => {
  const newStatus = card.status === 'disabled' ? 'unused' : 'disabled'
  const action = newStatus === 'disabled' ? '禁用' : '启用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}卡密 ${card.card_key} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await updateCardStatus(card.id, newStatus)
    ElMessage.success(`${action}成功`)
    loadCardList()
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
  loadCardList()
}

/**
 * 处理重置
 */
const handleReset = () => {
  filterForm.app_id = undefined
  filterForm.status = ''
  filterForm.keyword = ''
  pagination.page = 1
  loadCardList()
}

/**
 * 处理排序变化
 */
const handleSortChange = ({ prop, order }: any) => {
  // 可以根据需要实现排序逻辑
  console.log('排序变化:', prop, order)
}

/**
 * 处理页码变化
 */
const handlePageChange = (page: number) => {
  pagination.page = page
  loadCardList()
}

/**
 * 处理每页数量变化
 */
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadCardList()
}

/**
 * 生成卡密成功回调
 */
const handleGenerateSuccess = () => {
  loadCardList()
}

/**
 * 修改权限成功回调
 */
const handlePermissionSuccess = () => {
  loadCardList()
}

/**
 * 加载卡密列表
 */
const loadCardList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    
    if (filterForm.app_id) {
      params.app_id = filterForm.app_id
    }
    if (filterForm.status) {
      params.status = filterForm.status
    }
    if (filterForm.keyword) {
      params.keyword = filterForm.keyword
    }
    
    const data = await getCardList(params)
    cardList.value = data.cards
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('加载卡密列表失败')
    console.error('加载卡密列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 加载应用列表
 */
const loadAppList = async () => {
  try {
    const data = await getAppList()
    appList.value = data.apps
  } catch (error) {
    console.error('加载应用列表失败:', error)
  }
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadCardList()
  loadAppList()
})
</script>

<style scoped>
@reference "../../styles/index.css";
.card-management-container {
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

.header-actions {
}

.generate-btn {
  @apply px-6 py-2.5;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  @apply text-white font-medium rounded-xl;
  @apply shadow-lg shadow-blue-500/20;
  transition: all 0.3s ease;
}

.generate-btn:hover {
  @apply shadow-xl shadow-blue-500/30;
  transform: translateY(-2px);
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
  @apply w-64;
}

/* 表格区域 */
.table-section {
  @apply bg-white rounded-2xl p-6;
  @apply shadow-sm border border-gray-100;
}

.card-table {
  @apply w-full;
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

/* 过期时间单元格 */
.expire-time-cell {
  @apply flex items-center gap-2 text-sm text-gray-600;
}

/* 权限单元格 */
.permissions-cell {
  @apply flex flex-wrap gap-1;
}

.permission-tag {
  @apply bg-blue-50 text-blue-700 border-blue-200;
}

/* 操作按钮 */
.action-buttons {
  @apply flex gap-2;
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

  .header-actions {
    @apply w-full;
  }

  .generate-btn {
    @apply w-full;
  }

  .filter-form {
    @apply flex-col;
  }

  .filter-select,
  .filter-input {
    @apply w-full;
  }

  .action-buttons {
    @apply flex-col;
  }
}
</style>
