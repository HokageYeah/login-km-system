<template>
  <el-dialog
    v-model="dialogVisible"
    title="批量生成卡密"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 生成表单 -->
    <el-form
      v-if="!generated"
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      class="generate-form"
    >
      <el-form-item label="所属应用" prop="app_id">
        <el-select
          v-model="form.app_id"
          placeholder="请选择应用"
          class="w-full"
        >
          <el-option
            v-for="app in appList"
            :key="app.id"
            :label="app.app_name"
            :value="app.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="生成数量" prop="count">
        <el-input-number
          v-model="form.count"
          :min="1"
          :max="1000"
          placeholder="请输入生成数量"
          class="w-full"
        />
        <div class="form-tip">最多可生成 1000 个卡密</div>
      </el-form-item>

      <el-form-item label="过期时间" prop="expire_time">
        <el-date-picker
          v-model="form.expire_time"
          type="datetime"
          placeholder="选择过期时间"
          :disabled-date="disabledDate"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DDTHH:mm:ss"
          class="w-full"
        />
        <div class="expire-shortcut-group">
          <el-button
            v-for="shortcut in expireShortcutOptions"
            :key="shortcut.key"
            size="small"
            plain
            @click="handleExpireShortcutSelect(shortcut.key)"
          >
            {{ shortcut.label }}
          </el-button>
        </div>
        <div class="form-tip">必须大于当前时间</div>
      </el-form-item>

      <el-form-item label="最大设备数" prop="max_device_count">
        <el-input-number
          v-model="form.max_device_count"
          :min="1"
          :max="100"
          placeholder="请输入最大设备数"
          class="w-full"
        />
        <div class="form-tip">每个卡密最多可绑定的设备数量</div>
      </el-form-item>

      <el-form-item label="权限配置" prop="permissions">
        <el-select
          v-model="form.permissions"
          multiple
          placeholder="请选择权限"
          class="w-full"
          v-loading="loadingPermissions"
        >
          <el-option
            v-for="permission in availablePermissions"
            :key="permission.permission_key"
            :label="`${permission.permission_key} - ${permission.permission_name}`"
            :value="permission.permission_key"
            :disabled="permission.status === 'disabled'"
          >
            <div class="permission-option">
              <div class="option-main">
                <span class="permission-key">{{ permission.permission_key }} - {{ permission.permission_name }}</span>
                <el-tag v-if="permission.category" size="small" type="info" class="ml-2">
                  {{ permission.category }}
                </el-tag>
              </div>
              <!-- <div class="option-desc">{{ permission.description || '暂无描述' }}</div> -->
            </div>
          </el-option>
        </el-select>
        <div class="form-tip">可多选，至少选择一项权限</div>
      </el-form-item>

      <el-form-item label="备注信息" prop="remark">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="3"
          placeholder="请输入备注信息（可选）"
          maxlength="255"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <!-- 生成结果 -->
    <div v-else class="result-section">
      <div class="result-header">
        <el-icon class="success-icon" :size="48"><CircleCheckFilled /></el-icon>
        <h3 class="result-title">生成成功！</h3>
        <p class="result-subtitle">共生成 {{ generatedCards.length }} 个卡密</p>
      </div>

      <div class="result-actions">
        <el-button :icon="CopyDocument" @click="copyAllCards">
          复制全部
        </el-button>
        <el-button :icon="Download" @click="exportCards">
          导出为文本
        </el-button>
      </div>

      <div class="card-list">
        <div
          v-for="(card, index) in generatedCards"
          :key="index"
          class="card-item"
        >
          <span class="card-index">{{ index + 1 }}.</span>
          <span class="card-key">{{ card }}</span>
          <el-button
            :icon="CopyDocument"
            size="small"
            text
            @click="copyCard(card)"
            class="copy-btn"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          v-if="!generated"
          type="primary"
          :loading="loading"
          @click="handleGenerate"
        >
          生成卡密
        </el-button>
        <el-button
          v-else
          type="primary"
          @click="handleClose"
        >
          完成
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
/**
 * 生成卡密弹窗组件
 * @description 批量生成卡密的表单弹窗
 */
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { CircleCheckFilled, CopyDocument, Download } from '@element-plus/icons-vue'
import { generateCards } from '@/api/admin'
import { getFeaturePermissionList } from '@/api/feature-permission'
import {
  EXPIRE_SHORTCUT_OPTIONS,
  getExpireShortcutValue,
  type ExpireShortcutKey
} from '@/utils/expire-shortcuts'
import type { App, FeaturePermission } from '@/types'

/**
 * Props 定义
 */
interface Props {
  modelValue: boolean           // 弹窗显示状态
  appList: App[]                // 应用列表
}

const props = defineProps<Props>()

/**
 * Emits 定义
 */
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
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
const generated = ref(false)                            // 是否已生成
const generatedCards = ref<string[]>([])                // 生成的卡密列表
const formRef = ref<FormInstance>()                     // 表单引用
const availablePermissions = ref<FeaturePermission[]>([])  // 可用权限列表
const loadingPermissions = ref(false)                    // 加载权限列表状态
const expireShortcutOptions = EXPIRE_SHORTCUT_OPTIONS    // 过期时间快捷选项

/**
 * 表单数据
 */
const form = reactive({
  app_id: undefined as number | undefined,
  count: 10,
  expire_time: '',
  max_device_count: 1,
  permissions: [] as string[],
  remark: ''
})

/**
 * 表单验证规则
 */
const rules: FormRules = {
  app_id: [
    { required: true, message: '请选择应用', trigger: 'change' }
  ],
  count: [
    { required: true, message: '请输入生成数量', trigger: 'blur' },
    { type: 'number', min: 1, max: 1000, message: '数量范围：1-1000', trigger: 'blur' }
  ],
  expire_time: [
    { required: true, message: '请选择过期时间', trigger: 'change' }
  ],
  max_device_count: [
    { required: true, message: '请输入最大设备数', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '设备数范围：1-100', trigger: 'blur' }
  ],
  permissions: [
    { required: true, message: '请至少选择一项权限', trigger: 'change', type: 'array', min: 1 }
  ]
}

/**
 * 禁用过去的日期
 * @param time 日期时间
 * @returns 是否禁用
 */
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now()
}

/**
 * 处理快捷过期时间选择
 * @description 每次点击都以“当前时间”为基准重新计算目标时间，
 * 避免弹窗长时间停留后，按钮仍然沿用旧时间基准。
 * @param shortcutKey 快捷时间 key
 */
const handleExpireShortcutSelect = (shortcutKey: ExpireShortcutKey) => {
  const selectedShortcut = expireShortcutOptions.find(item => item.key === shortcutKey)
  const expireTimeValue = getExpireShortcutValue(shortcutKey)

  form.expire_time = expireTimeValue

  console.info('[卡密生成弹窗] 选择快捷过期时间', {
    shortcutKey,
    shortcutLabel: selectedShortcut?.label,
    expireTime: expireTimeValue
  })
}

/**
 * 加载权限列表
 */
const loadPermissions = async () => {
  loadingPermissions.value = true
  console.info('[卡密生成弹窗] 开始加载权限列表')
  try {
    const response = await getFeaturePermissionList({
      page: 1,
      size: 100  // 获取所有权限
    })
    // 只显示正常状态的权限
    availablePermissions.value = response.permissions.filter(p => p.status === 'normal')
    console.info('[卡密生成弹窗] 权限列表加载完成', {
      total: response.permissions.length,
      enabledCount: availablePermissions.value.length
    })
  } catch (error: any) {
    console.error('加载权限列表失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('加载权限列表失败')
    }
  } finally {
    loadingPermissions.value = false
  }
}

/**
 * 复制单个卡密
 * @param card 卡密字符串
 */
const copyCard = async (card: string) => {
  try {
    await navigator.clipboard.writeText(card)
    ElMessage.success('卡密已复制')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

/**
 * 复制全部卡密
 */
const copyAllCards = async () => {
  try {
    const text = generatedCards.value.join('\n')
    await navigator.clipboard.writeText(text)
    ElMessage.success('全部卡密已复制')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

/**
 * 导出卡密为文本文件
 */
const exportCards = () => {
  const text = generatedCards.value.join('\n')
  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `cards_${Date.now()}.txt`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

/**
 * 处理生成卡密
 */
const handleGenerate = async () => {
  if (!formRef.value) return
  
  try {
    // 验证表单
    await formRef.value.validate()
    
    loading.value = true

    console.info('[卡密生成弹窗] 开始批量生成卡密', {
      appId: form.app_id,
      count: form.count,
      expireTime: form.expire_time,
      maxDeviceCount: form.max_device_count,
      permissionCount: form.permissions.length
    })
    
    // 调用生成 API
    const data = await generateCards({
      app_id: form.app_id!,
      count: form.count,
      expire_time: form.expire_time,
      max_device_count: form.max_device_count,
      permissions: form.permissions,
      remark: form.remark || undefined
    })
    
    // 保存生成的卡密
    generatedCards.value = data.cards
    generated.value = true

    console.info('[卡密生成弹窗] 卡密生成成功', {
      generatedCount: data.cards.length,
      expireTime: form.expire_time
    })
    
    ElMessage.success(data.message || '生成成功')
    emit('success')
  } catch (error: any) {
    console.error('生成卡密失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('生成失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 处理关闭弹窗
 */
const handleClose = () => {
  console.info('[卡密生成弹窗] 关闭弹窗')
  dialogVisible.value = false
}

/**
 * 重置表单
 */
const resetForm = () => {
  console.info('[卡密生成弹窗] 重置表单状态')
  if (formRef.value) {
    formRef.value.resetFields()
  }
  generated.value = false
  generatedCards.value = []
  form.app_id = undefined
  form.count = 10
  form.expire_time = ''
  form.max_device_count = 1
  form.permissions = []
  form.remark = ''
  availablePermissions.value = []
}

/**
 * 监听弹窗打开，加载权限列表
 */
watch(dialogVisible, (newVal) => {
  if (newVal) {
    console.info('[卡密生成弹窗] 弹窗已打开，准备初始化数据')
    // 打开弹窗时加载权限列表
    loadPermissions()
  } else {
    setTimeout(resetForm, 300)
  }
})
</script>

<style scoped>
@reference "../../../styles/index.css";
.generate-form {
  @apply py-4;
}

.form-tip {
  @apply text-xs text-gray-500 mt-1;
}

.expire-shortcut-group {
  @apply flex flex-wrap gap-2 mt-3;
}

/* 权限选项样式 */
.permission-option {
  @apply w-full;
}

.option-main {
  @apply flex items-center justify-between;
  @apply mb-1;
}

.permission-key {
  @apply text-sm font-medium text-gray-900;
}

.option-desc {
  @apply text-xs text-gray-500;
  @apply mt-1;
}

/* 生成结果 */
.result-section {
  @apply py-4;
}

.result-header {
  @apply text-center mb-6;
}

.success-icon {
  @apply text-green-500 mb-4;
}

.result-title {
  @apply text-2xl font-bold text-gray-900 mb-2;
}

.result-subtitle {
  @apply text-base text-gray-600;
}

.result-actions {
  @apply flex justify-center gap-4 mb-6;
}

.card-list {
  @apply max-h-96 overflow-y-auto;
  @apply bg-gray-50 rounded-lg p-4;
  @apply space-y-2;
}

.card-item {
  @apply flex items-center gap-3;
  @apply bg-white rounded-lg p-3;
  @apply shadow-sm border border-gray-100;
  transition: all 0.2s ease;
}

.card-item:hover {
  @apply shadow-md border-blue-200;
}

.card-index {
  @apply text-sm font-medium text-gray-500;
  @apply w-8;
}

.card-key {
  @apply flex-1 font-mono text-sm font-medium text-gray-900;
}

.copy-btn {
  @apply text-blue-600;
}

.dialog-footer {
  @apply flex justify-end gap-3;
}
</style>
