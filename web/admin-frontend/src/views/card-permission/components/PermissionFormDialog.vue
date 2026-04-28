<template>
  <el-dialog
    v-model="dialogVisible"
    width="620px"
    :close-on-click-modal="false"
    :show-close="false"
    class="permission-form-root"
    @close="handleClose"
  >
    <!-- 自定义头部 -->
    <template #header>
      <div class="dialog-hero">
        <div class="dialog-hero-bg" />
        <div class="dialog-hero-content">
          <p class="dialog-eyebrow">{{ isEdit ? 'Edit Permission' : 'New Permission' }}</p>
          <h2 class="dialog-title">{{ isEdit ? '编辑功能权限' : '创建功能权限' }}</h2>
          <p class="dialog-desc" v-if="isEdit && editPermission">
            {{ editPermission.permission_key }}
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

    <div class="form-body">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-position="top"
        class="permission-form"
      >
        <!-- 基础信息 -->
        <div class="form-section">
          <div class="section-label">基础信息</div>

          <el-form-item prop="permission_key">
            <template #label>
              <span class="field-label">权限标识</span>
              <el-tooltip content="唯一标识符，只能包含字母、数字、下划线和连字符" placement="top">
                <el-icon :size="14" class="label-help"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input
              v-model="formData.permission_key"
              placeholder="如：wechat, ximalaya"
              clearable
              :disabled="isEdit"
            />
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
        </div>

        <!-- 关联与定价 -->
        <div class="form-section">
          <div class="section-label">关联与定价</div>

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
              <el-button link type="primary" @click="$emit('goToApp')">去创建应用</el-button>
            </div>
          </el-form-item>

          <el-form-item label="售卖价格（月）" prop="price">
            <div class="field-with-badge">
              <el-input-number
                v-model="formData.price"
                :min="0"
                :precision="2"
                :step="1"
                controls-position="right"
                class="field-control"
              />
              <div class="field-badge">元/月</div>
            </div>
          </el-form-item>
        </div>

        <!-- 显示设置 -->
        <div class="form-section">
          <div class="section-label">显示设置</div>

          <div class="settings-row">
            <el-form-item label="图标" prop="icon" class="settings-field">
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
                    <el-icon :size="18"><component :is="icon.value" /></el-icon>
                    <span>{{ icon.label }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item prop="sort_order" class="settings-field">
              <template #label>
                <span class="field-label">排序</span>
                <el-tooltip content="数字越小越靠前，默认为0" placement="top">
                  <el-icon :size="14" class="label-help"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number
                v-model="formData.sort_order"
                :min="0"
                :max="9999"
                controls-position="right"
                class="w-full"
              />
            </el-form-item>

            <el-form-item label="状态" prop="status" class="settings-field">
              <el-radio-group v-model="formData.status">
                <el-radio label="normal">正常</el-radio>
                <el-radio label="disabled">禁用</el-radio>
              </el-radio-group>
            </el-form-item>
          </div>
        </div>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" class="footer-btn-cancel">取消</el-button>
        <el-button
          type="primary"
          :loading="submitLoading"
          @click="handleSubmit"
          class="footer-btn-primary"
        >
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
/**
 * 创建/编辑功能权限弹窗
 * @description 复用同一弹窗，通过 isEdit 区分创建和编辑模式
 */
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Close, QuestionFilled } from '@element-plus/icons-vue'
import {
  createFeaturePermission,
  updateFeaturePermission
} from '@/api/feature-permission'
import type { App, FeaturePermission } from '@/types'

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

interface Props {
  modelValue: boolean
  isEdit: boolean
  editPermission: FeaturePermission | null
  appOptions: App[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
  goToApp: []
}>()

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const currentEditPermissionId = ref<number | null>(null)

const formData = reactive({
  permission_key: '',
  permission_name: '',
  app_id: undefined as number | undefined,
  description: '',
  price: 0,
  icon: '',
  sort_order: 0,
  status: 'normal' as string
})

const formRules: FormRules = {
  permission_key: [
    { required: true, message: '请输入权限标识', trigger: 'blur' },
    { min: 1, max: 100, message: '权限标识长度为1-100个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '权限标识只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ],
  permission_name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 1, max: 100, message: '权限名称长度为1-100个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述最多500个字符', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入售卖价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '售卖价格不能小于0', trigger: 'blur' }
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

const resetForm = () => {
  formData.permission_key = ''
  formData.permission_name = ''
  formData.app_id = undefined
  formData.description = ''
  formData.price = 0
  formData.icon = ''
  formData.sort_order = 0
  formData.status = 'normal'
  currentEditPermissionId.value = null
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      if (props.isEdit) {
        if (!currentEditPermissionId.value) {
          ElMessage.error('未找到当前编辑的权限记录')
          return
        }
        await updateFeaturePermission(currentEditPermissionId.value, { ...formData })
        ElMessage.success('更新成功')
      } else {
        await createFeaturePermission({
          ...formData,
          app_id: formData.app_id as number
        })
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      emit('success')
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

const handleClose = () => {
  dialogVisible.value = false
}

/**
 * 监听弹窗打开，填充表单数据
 */
watch(dialogVisible, (newVal) => {
  if (newVal) {
    if (props.isEdit && props.editPermission) {
      currentEditPermissionId.value = props.editPermission.id
      formData.permission_key = props.editPermission.permission_key
      formData.permission_name = props.editPermission.permission_name
      formData.app_id = props.editPermission.app_id
      formData.description = props.editPermission.description || ''
      formData.price = Number(props.editPermission.price ?? 0)
      formData.icon = props.editPermission.icon || ''
      formData.sort_order = props.editPermission.sort_order
      formData.status = props.editPermission.status
    } else {
      resetForm()
    }
  } else {
    setTimeout(() => {
      formRef.value?.resetFields()
      resetForm()
    }, 300)
  }
})
</script>

<style scoped>
@reference "../../../styles/index.css";

/* 弹窗覆写 */
:deep(.permission-form-root .el-dialog) {
  @apply rounded-3xl overflow-hidden border-0;
  box-shadow: 0 32px 80px rgba(15, 23, 42, 0.18), 0 0 0 1px rgba(148, 163, 184, 0.1);
}
:deep(.permission-form-root .el-dialog__header) { @apply p-0 m-0; }
:deep(.permission-form-root .el-dialog__body) { @apply px-6 py-5; max-height: 72vh; overflow-y: auto; }
:deep(.permission-form-root .el-dialog__footer) { @apply px-6 pb-5 pt-0; }

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

/* 表单 */
.form-body { @apply pt-1; }

.form-section {
  @apply rounded-2xl border border-slate-200/80 bg-white/60 p-4 mb-3;
  @apply backdrop-blur-sm;
}

.section-label {
  @apply text-xs font-semibold tracking-[0.12em] uppercase text-slate-400 mb-3;
}

.field-label { @apply mr-1; }
.label-help { @apply text-slate-400 cursor-help; }

/* 控件 + 右侧 badge */
.field-with-badge { @apply flex items-center gap-3 w-full; }
.field-control { @apply flex-1; }
.field-badge {
  @apply shrink-0 text-xs font-medium text-slate-400;
  @apply px-3 py-1.5 rounded-lg bg-slate-100/80 border border-slate-200/60;
}

/* 显示设置横排 */
.settings-row { @apply flex gap-4 flex-wrap; }
.settings-field { @apply flex-1 min-w-[140px]; }

/* 图标选项 */
.icon-option { @apply flex items-center gap-2; }

/* 无应用提示 */
.empty-app-tip { @apply mt-2 text-sm text-amber-600; }

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
