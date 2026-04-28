<template>
  <el-dialog
    v-model="dialogVisible"
    width="520px"
    :close-on-click-modal="false"
    :show-close="false"
    class="create-app-root"
    @close="handleClose"
  >
    <!-- 自定义头部 -->
    <template #header>
      <div class="dialog-hero">
        <div class="dialog-hero-bg" />
        <div class="dialog-hero-content">
          <p class="dialog-eyebrow">New Application</p>
          <h2 class="dialog-title">创建应用</h2>
          <p class="dialog-desc">创建新应用以接入卡密系统</p>
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
        :model="form"
        :rules="rules"
        label-position="top"
        class="app-form"
      >
        <!-- 基础信息 -->
        <div class="form-section">
          <div class="section-label">基础信息</div>

          <el-form-item prop="app_name">
            <template #label>
              <span class="field-label">应用名称</span>
              <el-tooltip content="应用的显示名称，2-50 个字符" placement="top">
                <el-icon :size="14" class="label-help"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input
              v-model="form.app_name"
              placeholder="如：我的应用"
              maxlength="50"
              show-word-limit
              clearable
            />
          </el-form-item>
        </div>

        <!-- 接入配置 -->
        <div class="form-section">
          <div class="section-label">接入配置</div>

          <el-form-item prop="app_key">
            <template #label>
              <span class="field-label">AppKey</span>
              <el-tooltip content="应用接入密钥，留空将自动生成" placement="top">
                <el-icon :size="14" class="label-help"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <div class="field-with-action">
              <el-input
                v-model="form.app_key"
                placeholder="留空则自动生成"
                maxlength="50"
                clearable
                class="field-control"
              />
              <el-button
                :icon="RefreshRight"
                @click="generateAppKey"
                class="field-action-btn"
              >
                生成
              </el-button>
            </div>
            <div class="field-tip">
              AppKey 用于应用接入鉴权，建议使用自动生成的随机密钥
            </div>
          </el-form-item>
        </div>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" class="footer-btn-cancel">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
          class="footer-btn-primary"
        >
          创建
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
/**
 * 创建应用弹窗组件
 * @description 自包含的创建应用表单弹窗
 */
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Close, RefreshRight, QuestionFilled } from '@element-plus/icons-vue'
import { createApp } from '@/api/app'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  app_name: '',
  app_key: ''
})

const rules: FormRules = {
  app_name: [
    { required: true, message: '请输入应用名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

const generateAppKey = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let key = ''
  for (let i = 0; i < 32; i++) {
    key += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  form.app_key = key
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    await createApp({
      app_name: form.app_name,
      app_key: form.app_key || undefined
    })

    ElMessage.success('创建成功')
    dialogVisible.value = false
    emit('success')
  } catch (error: any) {
    if (error !== false) {
      ElMessage.error(error.response?.data?.detail || '创建失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

const resetForm = () => {
  form.app_name = ''
  form.app_key = ''
}

watch(dialogVisible, (newVal) => {
  if (newVal) {
    resetForm()
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
:deep(.create-app-root .el-dialog) {
  @apply rounded-3xl overflow-hidden border-0;
  box-shadow: 0 32px 80px rgba(15, 23, 42, 0.18), 0 0 0 1px rgba(148, 163, 184, 0.1);
}
:deep(.create-app-root .el-dialog__header) { @apply p-0 m-0; }
:deep(.create-app-root .el-dialog__body) { @apply px-6 py-5; }
:deep(.create-app-root .el-dialog__footer) { @apply px-6 pb-5 pt-0; }

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
.dialog-desc { @apply text-sm text-blue-100; }
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

/* 输入框 + 生成按钮 */
.field-with-action { @apply flex gap-2 w-full; }
.field-control { @apply flex-1; }
.field-action-btn { @apply rounded-xl; }

/* 提示文字 */
.field-tip {
  @apply mt-2 text-xs text-slate-400 leading-5;
}

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
