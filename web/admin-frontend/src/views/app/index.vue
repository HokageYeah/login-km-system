<template>
  <div class="app-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">应用管理</h1>
        <p class="page-subtitle">管理系统中的所有应用，支持创建、启用/禁用操作</p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          :icon="Plus"
          @click="showCreateDialog"
          class="create-btn"
        >
          创建应用
        </el-button>
      </div>
    </div>

    <!-- 应用列表表格 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="appList"
        stripe
        class="app-table"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="app_name" label="应用名称" min-width="200">
          <template #default="{ row }">
            <div class="app-name-cell">
              <el-icon class="app-icon"><Grid /></el-icon>
              <span class="app-name-text">{{ row.app_name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="app_key" label="AppKey" min-width="250">
          <template #default="{ row }">
            <div class="app-key-cell">
              <span class="app-key-text">{{ row.app_key }}</span>
              <el-button
                :icon="CopyDocument"
                size="small"
                text
                @click="copyAppKey(row.app_key)"
                class="copy-btn"
              />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'normal' ? 'success' : 'danger'"
              effect="dark"
              class="status-tag"
            >
              {{ row.status === 'normal' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Clock /></el-icon>
              <span>{{ formatDateTime(row.created_at) }}</span>
            </div>
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
    </div>

    <!-- 创建应用弹窗 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建应用"
      width="500px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="create-form"
      >
        <el-form-item label="应用名称" prop="app_name">
          <el-input
            v-model="form.app_name"
            placeholder="请输入应用名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="AppKey" prop="app_key">
          <el-input
            v-model="form.app_key"
            placeholder="留空则自动生成"
            maxlength="50"
          >
            <template #append>
              <el-button :icon="Refresh" @click="generateAppKey">
                生成
              </el-button>
            </template>
          </el-input>
          <div class="form-tip">AppKey 用于应用接入，建议使用自动生成</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="submitting"
            @click="handleCreate"
          >
            创建
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 应用管理页面
 * @description 管理员管理系统中的所有应用
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  Grid,
  Clock,
  CopyDocument,
  CircleCheck,
  CircleClose,
  Refresh
} from '@element-plus/icons-vue'
import { getAppList, createApp, updateAppStatus } from '@/api/app'
import type { App } from '@/types'

/**
 * 状态定义
 */
const loading = ref(false)                              // 加载状态
const submitting = ref(false)                           // 提交状态
const appList = ref<App[]>([])                          // 应用列表
const createDialogVisible = ref(false)                  // 创建弹窗显示状态
const formRef = ref<FormInstance>()                     // 表单引用

/**
 * 表单数据
 */
const form = reactive({
  app_name: '',
  app_key: ''
})

/**
 * 表单验证规则
 */
const rules: FormRules = {
  app_name: [
    { required: true, message: '请输入应用名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
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
 * 复制 AppKey
 * @param appKey AppKey 字符串
 */
const copyAppKey = async (appKey: string) => {
  try {
    await navigator.clipboard.writeText(appKey)
    ElMessage.success('AppKey 已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

/**
 * 生成随机 AppKey
 */
const generateAppKey = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let appKey = ''
  for (let i = 0; i < 32; i++) {
    appKey += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  form.app_key = appKey
}

/**
 * 显示创建弹窗
 */
const showCreateDialog = () => {
  createDialogVisible.value = true
}

/**
 * 处理创建应用
 */
const handleCreate = async () => {
  if (!formRef.value) return
  
  try {
    // 验证表单
    await formRef.value.validate()
    
    submitting.value = true
    
    // 调用创建 API
    const data = await createApp({
      app_name: form.app_name,
      app_key: form.app_key || undefined
    })
    
    ElMessage.success('创建成功')
    createDialogVisible.value = false
    loadAppList()
  } catch (error: any) {
    console.error('创建应用失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('创建失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

/**
 * 处理状态变更
 * @param app 应用信息
 */
const handleStatusChange = async (app: App) => {
  const newStatus = app.status === 'disabled' ? 'normal' : 'disabled'
  const action = newStatus === 'disabled' ? '禁用' : '启用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}应用 ${app.app_name} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true,
        message: `
          <div>
            <p>应用名称：<strong>${app.app_name}</strong></p>
            <p>AppKey：<strong>${app.app_key}</strong></p>
            <p style="color: #f56c6c; margin-top: 10px;">
              ${newStatus === 'disabled' ? '禁用后该应用将无法使用' : '启用后该应用将恢复正常使用'}
            </p>
          </div>
        `
      }
    )
    
    await updateAppStatus(app.id, newStatus)
    ElMessage.success(`${action}成功`)
    loadAppList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`${action}失败`)
    }
  }
}

/**
 * 处理弹窗关闭
 */
const handleDialogClose = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  form.app_name = ''
  form.app_key = ''
}

/**
 * 加载应用列表
 */
const loadAppList = async () => {
  loading.value = true
  try {
    const data = await getAppList()
    appList.value = data.apps
  } catch (error) {
    ElMessage.error('加载应用列表失败')
    console.error('加载应用列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadAppList()
})
</script>

<style scoped>
@reference "../../styles/index.css";
.app-management-container {
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

.create-btn {
  @apply px-6 py-2.5;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  @apply text-white font-medium rounded-xl;
  @apply shadow-lg shadow-blue-500/20;
  transition: all 0.3s ease;
}

.create-btn:hover {
  @apply shadow-xl shadow-blue-500/30;
  transform: translateY(-2px);
}

/* 表格区域 */
.table-section {
  @apply bg-white rounded-2xl p-6;
  @apply shadow-sm border border-gray-100;
}

.app-table {
  @apply w-full;
}

/* 应用名称单元格 */
.app-name-cell {
  @apply flex items-center gap-2;
}

.app-icon {
  @apply text-purple-600;
}

.app-name-text {
  @apply font-medium text-gray-900;
}

/* AppKey单元格 */
.app-key-cell {
  @apply flex items-center gap-2;
}

.app-key-text {
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

/* 创建表单 */
.create-form {
  @apply py-4;
}

.form-tip {
  @apply text-xs text-gray-500 mt-1;
}

.dialog-footer {
  @apply flex justify-end gap-3;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .page-header {
    @apply flex-col gap-4;
  }

  .header-actions {
    @apply w-full;
  }

  .create-btn {
    @apply w-full;
  }
}
</style>
