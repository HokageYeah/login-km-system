<template>
  <div class="user-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">管理系统中的所有用户，支持查询、封禁/解封操作</p>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="选择状态"
            clearable
            class="filter-select"
          >
            <el-option label="正常" value="normal" />
            <el-option label="封禁" value="banned" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索用户名"
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

    <!-- 用户列表表格 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="userList"
        stripe
        class="user-table"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="username" label="用户名" min-width="150">
          <template #default="{ row }">
            <div class="username-cell">
              <el-icon class="user-icon"><User /></el-icon>
              <span class="username-text">{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.role === 'admin' ? 'danger' : 'primary'"
              effect="dark"
            >
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'normal' ? 'success' : 'danger'"
              effect="dark"
              class="status-tag"
            >
              {{ row.status === 'normal' ? '正常' : '封禁' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="card_count" label="有效卡密" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">
              {{ row.card_count || 0 }}
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
        
        <el-table-column prop="last_login_at" label="最后登录" width="180">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Clock /></el-icon>
              <span>{{ formatDateTime(row.last_login_at) }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.role !== 'admin'"
              size="small"
              :type="row.status === 'banned' ? 'success' : 'danger'"
              :icon="row.status === 'banned' ? CircleCheck : CircleClose"
              @click="handleStatusChange(row)"
            >
              {{ row.status === 'banned' ? '解封' : '封禁' }}
            </el-button>
            <el-tag v-else type="info" size="small">
              管理员
            </el-tag>
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
 * 用户管理页面
 * @description 管理员管理系统中的所有用户
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  User,
  Clock,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'
import { getUserList, updateUserStatus } from '@/api/admin'
import type { User as UserType } from '@/types'

/**
 * 状态定义
 */
const loading = ref(false)                              // 加载状态
const userList = ref<UserType[]>([])                    // 用户列表

/**
 * 筛选表单
 */
const filterForm = reactive({
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
 * 处理状态变更
 * @param user 用户信息
 */
const handleStatusChange = async (user: UserType) => {
  const newStatus = user.status === 'banned' ? 'normal' : 'banned'
  const action = newStatus === 'banned' ? '封禁' : '解封'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 ${user.username} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true,
        message: `
          <div>
            <p>用户名：<strong>${user.username}</strong></p>
            <p>当前状态：<strong>${user.status === 'normal' ? '正常' : '封禁'}</strong></p>
            <p style="color: #f56c6c; margin-top: 10px;">
              ${newStatus === 'banned' ? '封禁后该用户将无法登录系统' : '解封后该用户将恢复正常访问'}
            </p>
          </div>
        `
      }
    )
    
    await updateUserStatus(user.id, newStatus)
    ElMessage.success(`${action}成功`)
    loadUserList()
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
  loadUserList()
}

/**
 * 处理重置
 */
const handleReset = () => {
  filterForm.status = ''
  filterForm.keyword = ''
  pagination.page = 1
  loadUserList()
}

/**
 * 处理页码变化
 */
const handlePageChange = (page: number) => {
  pagination.page = page
  loadUserList()
}

/**
 * 处理每页数量变化
 */
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadUserList()
}

/**
 * 加载用户列表
 */
const loadUserList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    
    if (filterForm.status) {
      params.status = filterForm.status
    }
    if (filterForm.keyword) {
      params.keyword = filterForm.keyword
    }
    
    const data = await getUserList(params)
    userList.value = data.users
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('加载用户列表失败')
    console.error('加载用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadUserList()
})
</script>

<style scoped>
@reference "../../styles/index.css";
.user-management-container {
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
  @apply w-64;
}

/* 表格区域 */
.table-section {
  @apply bg-white rounded-2xl p-6;
  @apply shadow-sm border border-gray-100;
}

.user-table {
  @apply w-full;
}

/* 用户名单元格 */
.username-cell {
  @apply flex items-center gap-2;
}

.user-icon {
  @apply text-blue-600;
}

.username-text {
  @apply font-medium text-gray-900;
}

/* 状态标签 */
.status-tag {
  @apply font-medium;
}

/* 时间单元格 */
.time-cell {
  @apply flex items-center gap-2 text-sm text-gray-600;
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
