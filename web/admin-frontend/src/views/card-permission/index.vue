<template>
  <div class="permission-container">
    <!-- 页面标题 -->
    <div class="permission-header">
      <div>
        <h1 class="permission-title">功能权限管理</h1>
        <p class="permission-subtitle">按应用维度配置卡密可使用的功能权限</p>
      </div>
      <div class="header-actions">
        <el-button
          :icon="Download"
          :loading="exportLoading"
          :disabled="selectedPermissionKeys.length === 0"
          @click="handleExport"
          class="export-btn"
        >
          导出选中权限
        </el-button>
        <el-button
          :icon="Upload"
          :loading="importLoading"
          @click="triggerImport"
          class="import-btn"
        >
          导入权限文件
        </el-button>
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
          v-model="filters.app_id"
          placeholder="选择所属应用"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option
            v-for="app in appOptions"
            :key="app.id"
            :label="app.app_name"
            :value="app.id"
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
      <div v-if="selectedPermissions.length > 0" class="batch-actions-bar">
        <div class="selected-info">
          <span>已选择 <strong>{{ selectedPermissions.length }}</strong> 个功能权限</span>
        </div>
        <div class="action-buttons">
          <el-button
            type="danger"
            :icon="Delete"
            @click="handleBatchDelete"
          >
            批量删除
          </el-button>
          <el-button @click="clearSelection">
            取消选择
          </el-button>
        </div>
      </div>

      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="permissions"
        row-key="permission_key"
        stripe
        class="permission-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column
          type="selection"
          width="56"
          align="center"
          reserve-selection
        />
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
        <el-table-column prop="app_name" label="所属应用" min-width="160">
          <template #default="{ row }">
            <el-tag
              v-if="row.app_name"
              size="small"
              effect="plain"
              :style="getAppBadgeStyle(row)"
            >
              {{ row.app_name }}
            </el-tag>
            <el-tag v-else type="warning" size="small" effect="plain">
              未绑定应用
            </el-tag>
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

        <el-form-item label="所属应用" prop="app_id">
          <el-select
            v-model="formData.app_id"
            placeholder="请选择所属应用"
            filterable
            clearable
            class="w-full"
          >
            <el-option
              v-for="app in appOptions"
              :key="app.id"
              :label="app.app_name"
              :value="app.id"
            />
          </el-select>
          <div v-if="appOptions.length === 0" class="empty-app-tip">
            当前还没有应用，请先去应用管理中创建应用后再创建权限。
            <el-button link type="primary" @click="goToAppManagement">去创建应用</el-button>
          </div>
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
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules
} from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  QuestionFilled,
  Upload,
  Delete,
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
  createFeaturePermission,
  updateFeaturePermission,
  deleteFeaturePermission,
  batchDeleteFeaturePermissions,
  exportFeaturePermissions,
  importFeaturePermissions
} from '@/api/feature-permission'
import { getAppList } from '@/api/app'
import type { App, FeaturePermission } from '@/types'
import { getAppTagStyle } from '@/utils/app-tag'
import type { ElTable } from 'element-plus'

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

const router = useRouter()
const route = useRoute()

/**
 * 状态定义
 */
const loading = ref(false)
const exportLoading = ref(false)
const importLoading = ref(false)
const permissions = ref<FeaturePermission[]>([])
const appOptions = ref<App[]>([])
const selectedPermissionKeys = ref<string[]>([])
const selectedPermissions = ref<FeaturePermission[]>([])
const tableRef = ref<InstanceType<typeof ElTable>>()

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
  app_id: undefined as number | undefined,
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
const currentEditPermissionId = ref<number | null>(null)

/**
 * 表单数据
 */
const formData = ref<any>({
  permission_key: '',
  permission_name: '',
  app_id: undefined as number | undefined,
  description: '',
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
  app_id: [
    { required: true, message: '请选择所属应用', trigger: 'change' }
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
    console.info('[功能权限管理] 开始加载权限列表', {
      page: pagination.value.page,
      size: pagination.value.size,
      app_id: filters.value.app_id,
      status: filters.value.status,
      keyword: filters.value.keyword
    })
    const data = await getFeaturePermissionList({
      page: pagination.value.page,
      size: pagination.value.size,
      app_id: filters.value.app_id,
      status: filters.value.status || undefined,
      keyword: filters.value.keyword || undefined
    })
    permissions.value = data.permissions || []
    pagination.value.total = data.total
    selectedPermissions.value = selectedPermissions.value.filter((selectedPermission) =>
      permissions.value.some((permission) => permission.id === selectedPermission.id)
    )
    selectedPermissionKeys.value = selectedPermissionKeys.value.filter((permissionKey) =>
      permissions.value.some((permission) => permission.permission_key === permissionKey)
    )
    console.info('[功能权限管理] 权限列表加载完成', {
      total: pagination.value.total,
      currentPageCount: permissions.value.length
    })
  } catch (error: any) {
    console.error('[功能权限管理] 加载权限列表失败', error)
    ElMessage.error(error.response?.data?.detail || '加载权限列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 加载应用列表
 */
const loadApps = async () => {
  try {
    console.info('[功能权限管理] 开始加载应用列表')
    const data = await getAppList()
    appOptions.value = data.apps || []
    console.info('[功能权限管理] 应用列表加载完成', {
      total: appOptions.value.length
    })
  } catch (error: any) {
    console.error('[功能权限管理] 加载应用列表失败', error)
    ElMessage.error('加载应用列表失败')
  }
}

/**
 * 根据路由同步筛选条件
 * @description 应用管理页跳转时会携带 app_id，这里统一做落地，避免每个跳转入口各写一份解析逻辑。
 */
const syncFilterFromRoute = () => {
  const routeAppId = route.query.app_id
  if (typeof routeAppId === 'string' && routeAppId) {
    const parsedAppId = Number(routeAppId)
    filters.value.app_id = Number.isNaN(parsedAppId) ? undefined : parsedAppId
    return
  }

  filters.value.app_id = undefined
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
  console.info('[功能权限管理] 手动刷新权限页数据')
  loadApps()
  loadPermissions()
}

/**
 * 处理表格勾选变化
 * @description 导出能力以勾选项为准，因此统一维护当前页面已选权限标识。
 */
const handleSelectionChange = (selectedRows: FeaturePermission[]) => {
  selectedPermissions.value = selectedRows
  selectedPermissionKeys.value = selectedRows.map((row) => row.permission_key)
  console.info('[功能权限管理] 勾选权限变化', {
    selectedPermissionKeys: selectedPermissionKeys.value
  })
}

/**
 * 清除表格勾选
 */
const clearSelection = () => {
  tableRef.value?.clearSelection()
  selectedPermissions.value = []
  selectedPermissionKeys.value = []
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
  if (appOptions.value.length === 0) {
    console.warn('[功能权限管理] 当前没有应用，禁止创建权限并提示跳转')
    ElMessageBox.confirm(
      '当前还没有应用，权限必须绑定到应用后才能创建。现在跳转到应用管理页吗？',
      '请先创建应用',
      {
        confirmButtonText: '去创建应用',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      goToAppManagement()
    }).catch(() => {
      console.info('[功能权限管理] 用户取消跳转到应用管理页')
    })
    return
  }

  dialogTitle.value = '创建功能权限'
  isEdit.value = false
  currentEditPermissionId.value = null
  formData.value = {
    permission_key: '',
    permission_name: '',
    app_id: undefined,
    description: '',
    icon: '',
    sort_order: 0,
    status: 'normal'
  }
  console.info('[功能权限管理] 打开创建权限弹窗')
  dialogVisible.value = true
}

/**
 * 编辑权限
 */
const handleEdit = (permission: FeaturePermission) => {
  dialogTitle.value = '编辑功能权限'
  isEdit.value = true
  currentEditPermissionId.value = permission.id
  formData.value = {
    permission_key: permission.permission_key,
    permission_name: permission.permission_name,
    app_id: permission.app_id,
    description: permission.description || '',
    icon: permission.icon || '',
    sort_order: permission.sort_order,
    status: permission.status
  }
  console.info('[功能权限管理] 打开编辑权限弹窗', {
    permission_id: permission.id,
    permission_key: permission.permission_key,
    app_id: permission.app_id
  })
  dialogVisible.value = true
}

/**
 * 跳转到应用管理页
 */
const goToAppManagement = () => {
  console.info('[功能权限管理] 跳转到应用管理页')
  router.push('/apps')
}

/**
 * 获取应用徽标样式
 */
const getAppBadgeStyle = (permission: FeaturePermission) => getAppTagStyle(
  permission.app_key,
  permission.app_name
)

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
    console.info('[功能权限管理] 删除权限成功', {
      permission_id: permission.id,
      permission_key: permission.permission_key
    })
    ElMessage.success('删除成功')
    await loadPermissions()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('[功能权限管理] 删除权限失败', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

/**
 * 批量删除功能权限
 */
const handleBatchDelete = async () => {
  if (selectedPermissions.value.length === 0) {
    ElMessage.warning('请先选择要删除的功能权限')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedPermissions.value.length} 个功能权限吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true,
        message: `
          <div>
            <p>即将删除 <strong>${selectedPermissions.value.length}</strong> 个功能权限</p>
            <p style="color: #f56c6c; margin-top: 10px;">
              <strong>警告：</strong>删除操作不可恢复！
            </p>
            <p style="color: #f56c6c;">
              删除的是权限元数据，历史卡密中的旧 permission_key 不会自动清理。
            </p>
          </div>
        `
      }
    )

    const result = await batchDeleteFeaturePermissions(
      selectedPermissions.value.map((permission) => permission.id)
    )
    ElMessage.success(result.message)
    clearSelection()
    await loadPermissions()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('[功能权限管理] 批量删除功能权限失败', error)
      ElMessage.error(error.response?.data?.detail || '批量删除失败')
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
        if (!currentEditPermissionId.value) {
          ElMessage.error('未找到当前编辑的权限记录')
          return
        }

        console.info('[功能权限管理] 开始更新权限', {
          permission_id: currentEditPermissionId.value,
          formData: formData.value
        })
        await updateFeaturePermission(currentEditPermissionId.value, formData.value)
        ElMessage.success('更新成功')
      } else {
        console.info('[功能权限管理] 开始创建权限', {
          formData: formData.value
        })
        await createFeaturePermission(formData.value)
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      await loadPermissions()
    } catch (error: any) {
      console.error('[功能权限管理] 提交权限表单失败', error)
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

/**
 * 构建导出文件名
 * @description 浏览器侧兜底生成文件名，避免部分浏览器拿不到响应头时无法命名文件。
 */
const buildExportFilename = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  return `feature_permissions_${year}${month}${day}_${hours}${minutes}${seconds}.json`
}

/**
 * 下载导出文件
 */
const downloadBlobFile = (blob: Blob, fileName: string) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * 导出勾选权限
 * @description 仅导出用户明确勾选的权限，避免分页或筛选造成误导出。
 */
const handleExport = async () => {
  if (selectedPermissionKeys.value.length === 0) {
    ElMessage.warning('请先勾选要导出的权限')
    return
  }

  exportLoading.value = true
  try {
    console.info('[功能权限管理] 开始导出权限', {
      selectedPermissionKeys: selectedPermissionKeys.value
    })
    const blob = await exportFeaturePermissions(selectedPermissionKeys.value)

    downloadBlobFile(blob, buildExportFilename())
    ElMessage.success(`导出成功，共导出 ${selectedPermissionKeys.value.length} 条权限`)
  } catch (error: any) {
    console.error('[功能权限管理] 导出权限失败', error)
    ElMessage.error(error.response?.data?.detail || '导出权限失败')
  } finally {
    exportLoading.value = false
  }
}

/**
 * 触发导入文件选择
 * @description 直接在用户点击事件里动态创建 input，兼容性比隐藏 input 和组件代理更稳定。
 */
const triggerImport = () => {
  if (importLoading.value) {
    return
  }

  const fileInput = document.createElement('input')
  fileInput.type = 'file'
  fileInput.accept = '.json,application/json'

  fileInput.onchange = async () => {
    const selectedFile = fileInput.files?.[0]
    if (!selectedFile) {
      return
    }

    await importPermissionFile(selectedFile)
  }

  fileInput.click()
}

/**
 * 导入权限文件
 */
const importPermissionFile = async (selectedFile: File) => {
  importLoading.value = true
  try {
    console.info('[功能权限管理] 开始导入权限文件', {
      fileName: selectedFile.name,
      fileSize: selectedFile.size
    })
    const result = await importFeaturePermissions(selectedFile)
    ElMessage.success(
      `导入成功，共处理 ${result.total_count} 条，新增 ${result.created_count} 条，更新 ${result.updated_count} 条，自动创建应用 ${result.created_app_count} 个`
    )
    pagination.value.page = 1
    await loadPermissions()
    await loadApps()
  } catch (error: any) {
    console.error('[功能权限管理] 导入权限失败', error)
    ElMessage.error(error.response?.data?.detail || '导入权限失败')
  } finally {
    importLoading.value = false
  }
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
  syncFilterFromRoute()
  loadApps()
  loadPermissions()
})

watch(
  () => route.query.app_id,
  () => {
    syncFilterFromRoute()
    pagination.value.page = 1
    loadPermissions()
  }
)
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

.export-btn {
  @apply px-5 py-2.5 rounded-xl border border-blue-100;
  @apply bg-white text-blue-600 font-medium;
}

.import-btn {
  @apply px-5 py-2.5 rounded-xl border border-emerald-100;
  @apply bg-emerald-50 text-emerald-700 font-medium;
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

.batch-actions-bar {
  @apply flex items-center justify-between mb-4 px-4 py-3;
  @apply rounded-xl border border-red-100 bg-red-50;
}

.selected-info {
  @apply text-sm text-gray-700;
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

.empty-app-tip {
  @apply mt-2 text-sm text-amber-600;
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
