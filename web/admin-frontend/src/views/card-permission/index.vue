<template>
  <div class="permission-container">
    <!-- 页面标题 -->
    <div class="permission-header">
      <div>
        <h1 class="permission-title">功能权限管理</h1>
        <p class="permission-subtitle">配置卡密可使用的功能权限</p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          :icon="Plus"
          @click="handleCreate"
          class="create-btn"
        >
          创建权限
        </el-button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-card">
      <div class="filter-row">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索权限标识或名称"
          clearable
          :prefix-icon="Search"
          class="filter-input"
          @input="handleSearch"
        />
        <el-select
          v-model="filters.category"
          placeholder="选择分类"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option
            v-for="category in categories"
            :key="category"
            :label="category"
            :value="category"
          />
        </el-select>
        <el-select
          v-model="filters.status"
          placeholder="选择状态"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option label="正常" value="normal" />
          <el-option label="禁用" value="disabled" />
        </el-select>
        <el-button
          :icon="Refresh"
          @click="handleRefresh"
          class="refresh-btn"
        >
          刷新
        </el-button>
      </div>
    </div>

    <!-- 权限列表 -->
    <div class="permission-list">
      <el-table
        v-loading="loading"
        :data="permissions"
        stripe
        class="permission-table"
      >
        <el-table-column prop="permission_key" label="权限标识" min-width="150">
          <template #default="{ row }">
            <el-tag type="primary" size="small" class="permission-tag">
              {{ row.permission_key }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="permission_name" label="权限名称" min-width="150">
          <template #default="{ row }">
            <div class="name-cell">
              <el-icon v-if="row.icon" :size="20" class="name-icon">
                <component :is="row.icon" />
              </el-icon>
              <span>{{ row.permission_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" min-width="120">
          <template #default="{ row }">
            <el-tag v-if="row.category" type="info" size="small" effect="plain">
              {{ row.category }}
            </el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'normal' ? 'success' : 'danger'"
              size="small"
              class="status-tag"
            >
              {{ row.status === 'normal' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                type="primary"
                size="small"
                link
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                link
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 创建/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
      class="permission-dialog"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="权限标识" prop="permission_key">
          <el-input
            v-model="formData.permission_key"
            placeholder="如：wechat, ximalaya"
            clearable
            :disabled="isEdit"
          />
          <template #label>
            <span class="form-label">权限标识</span>
            <el-tooltip content="权限的唯一标识符，只能包含字母、数字、下划线和连字符" placement="top">
              <el-icon :size="14" class="label-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
        </el-form-item>

        <el-form-item label="权限名称" prop="permission_name">
          <el-input
            v-model="formData.permission_name"
            placeholder="如：微信抓取、喜马拉雅播放"
            clearable
          />
        </el-form-item>

        <el-form-item label="权限描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="描述该功能权限的用途"
            clearable
          />
        </el-form-item>

        <el-form-item label="权限分类" prop="category">
          <el-select
            v-model="formData.category"
            placeholder="选择或输入分类"
            filterable
            allow-create
            clearable
          >
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="图标" prop="icon">
          <el-select
            v-model="formData.icon"
            placeholder="选择图标"
            clearable
            filterable
          >
            <el-option
              v-for="icon in iconOptions"
              :key="icon.value"
              :label="icon.label"
              :value="icon.value"
            >
              <div class="icon-option">
                <el-icon :size="20"><component :is="icon.value" /></el-icon>
                <span>{{ icon.label }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number
            v-model="formData.sort_order"
            :min="0"
            :max="9999"
            controls-position="right"
            class="w-full"
          />
          <template #label>
            <span class="form-label">排序</span>
            <el-tooltip content="数字越小越靠前，默认为0" placement="top">
              <el-icon :size="14" class="label-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio label="normal">正常</el-radio>
            <el-radio label="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="submitLoading"
          @click="handleSubmit"
        >
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 功能权限管理页面
 * @description 管理系统中的功能权限，支持增删改查
 */
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  QuestionFilled,
  ChatDotRound,
  Document,
  VideoPlay,
  Download,
  Picture,
  Location,
  Share,
  Setting
} from '@element-plus/icons-vue'
import {
  getFeaturePermissionList,
  getPermissionCategories,
  createFeaturePermission,
  updateFeaturePermission,
  deleteFeaturePermission
} from '@/api/feature-permission'
import type { FeaturePermission } from '@/types'

/**
 * 图标选项
 */
const iconOptions = [
  { label: '聊天', value: 'ChatDotRound' },
  { label: '文档', value: 'Document' },
  { label: '视频播放', value: 'VideoPlay' },
  { label: '下载', value: 'Download' },
  { label: '图片', value: 'Picture' },
  { label: '定位', value: 'Location' },
  { label: '分享', value: 'Share' },
  { label: '设置', value: 'Setting' }
]

/**
 * 状态定义
 */
const loading = ref(false)
const permissions = ref<FeaturePermission[]>([])
const categories = ref<string[]>([])

/**
 * 分页参数
 */
const pagination = ref({
  page: 1,
  size: 20,
  total: 0
})

/**
 * 筛选条件
 */
const filters = ref({
  keyword: '',
  category: '',
  status: ''
})

/**
 * 弹窗相关
 */
const dialogVisible = ref(false)
const dialogTitle = ref('创建功能权限')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

/**
 * 表单数据
 */
const formData = ref({
  permission_key: '',
  permission_name: '',
  description: '',
  category: '',
  icon: '',
  sort_order: 0,
  status: 'normal'
})

/**
 * 表单验证规则
 */
const formRules: FormRules = {
  permission_key: [
    { required: true, message: '请输入权限标识', trigger: 'blur' },
    { min: 1, max: 100, message: '权限标识长度为1-100个字符', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_-]+$/,
      message: '权限标识只能包含字母、数字、下划线和连字符',
      trigger: 'blur'
    }
  ],
  permission_name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 1, max: 100, message: '权限名称长度为1-100个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述最多500个字符', trigger: 'blur' }
  ],
  category: [
    { max: 50, message: '分类最多50个字符', trigger: 'blur' }
  ],
  sort_order: [
    { type: 'number', message: '排序必须为数字', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

/**
 * 加载权限列表
 */
const loadPermissions = async () => {
  loading.value = true
  try {
    const response = await getFeaturePermissionList({
      page: pagination.value.page,
      size: pagination.value.size,
      category: filters.value.category || undefined,
      status: filters.value.status || undefined,
      keyword: filters.value.keyword || undefined
    })
    const data = response.data || response
    permissions.value = data.permissions || []
    pagination.value.total = data.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载权限列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 加载权限分类
 */
const loadCategories = async () => {
  try {
    const response = await getPermissionCategories()
    const data = response.data || response
    categories.value = data.categories || []
  } catch (error: any) {
    console.error('加载分类失败:', error)
  }
}

/**
 * 搜索处理
 */
const handleSearch = () => {
  pagination.value.page = 1
  loadPermissions()
}

/**
 * 筛选处理
 */
const handleFilter = () => {
  pagination.value.page = 1
  loadPermissions()
}

/**
 * 刷新
 */
const handleRefresh = () => {
  loadPermissions()
}

/**
 * 分页大小改变
 */
const handleSizeChange = (size: number) => {
  pagination.value.size = size
  loadPermissions()
}

/**
 * 页码改变
 */
const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadPermissions()
}

/**
 * 创建权限
 */
const handleCreate = () => {
  dialogTitle.value = '创建功能权限'
  isEdit.value = false
  formData.value = {
    permission_key: '',
    permission_name: '',
    description: '',
    category: '',
    icon: '',
    sort_order: 0,
    status: 'normal'
  }
  dialogVisible.value = true
}

/**
 * 编辑权限
 */
const handleEdit = (permission: FeaturePermission) => {
  dialogTitle.value = '编辑功能权限'
  isEdit.value = true
  formData.value = {
    permission_key: permission.permission_key,
    permission_name: permission.permission_name,
    description: permission.description || '',
    category: permission.category || '',
    icon: permission.icon || '',
    sort_order: permission.sort_order,
    status: permission.status
  }
  dialogVisible.value = true
}

/**
 * 删除权限
 */
const handleDelete = async (permission: FeaturePermission) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除功能权限"${permission.permission_name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteFeaturePermission(permission.id)
    ElMessage.success('删除成功')
    await loadPermissions()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

/**
 * 提交表单
 */
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      if (isEdit.value) {
        // 编辑：需要找到当前编辑的权限ID
        const currentPermission = permissions.value.find(
          p => p.permission_key === formData.value.permission_key
        )
        if (currentPermission) {
          await updateFeaturePermission(currentPermission.id, formData.value)
          ElMessage.success('更新成功')
        }
      } else {
        // 创建
        await createFeaturePermission(formData.value)
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      await loadPermissions()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

/**
 * 格式化日期
 */
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadPermissions()
  loadCategories()
})
</script>

<style scoped>
@reference "../../styles/index.css";
.permission-container {
  @apply w-full h-full;
  @apply p-8;
  @apply bg-gradient-to-br from-gray-50 to-gray-100;
  min-height: calc(100vh - 64px);
}

/* 页面头部 */
.permission-header {
  @apply flex justify-between items-center mb-6;
}

.permission-title {
  @apply text-3xl font-bold text-gray-900;
  @apply mb-2;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.permission-subtitle {
  @apply text-base text-gray-600;
}

.header-actions {
  @apply flex gap-4;
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

/* 筛选卡片 */
.filter-card {
  @apply bg-white rounded-2xl p-6;
  @apply shadow-sm border border-gray-100;
  @apply mb-6;
}

.filter-row {
  @apply flex gap-4 items-center;
}

.filter-input {
  @apply flex-1;
}

.filter-select {
  @apply w-40;
}

.refresh-btn {
  @apply px-4;
}

/* 权限列表 */
.permission-list {
  @apply bg-white rounded-2xl p-6;
  @apply shadow-sm border border-gray-100;
}

.permission-table {
  @apply w-full;
}

.permission-tag {
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

.name-cell {
  @apply flex items-center gap-2;
}

.name-icon {
  @apply text-blue-600;
}

.status-tag {
  @apply font-medium;
}

.text-muted {
  @apply text-gray-400;
}

.action-buttons {
  @apply flex gap-2;
}

/* 分页 */
.pagination-wrapper {
  @apply flex justify-center mt-6;
}

/* 表单标签 */
.form-label {
  @apply flex items-center gap-1;
}

.label-icon {
  @apply text-gray-400 cursor-help;
}

/* 弹窗样式 */
.permission-dialog {
  :deep(.el-dialog__header) {
    @apply border-b border-gray-100 pb-4;
  }

  :deep(.el-dialog__body) {
    @apply pt-4;
  }

  :deep(.el-form-item__label) {
    @apply font-medium text-gray-700;
  }
}

/* 图标选项 */
.icon-option {
  @apply flex items-center gap-2;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .permission-container {
    @apply p-4;
  }

  .permission-header {
    @apply flex-col items-start gap-4;
  }

  .filter-row {
    @apply flex-col items-stretch;
  }

  .filter-select {
    @apply w-full;
  }
}
</style>
