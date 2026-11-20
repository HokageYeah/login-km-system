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

/*
 * 创建应用弹窗（Brutalism 改版）：
 * 全局主题已接管 el-dialog 的黑框/硬阴影/直角外观，
 * 这里只保留自定义头部的黑色 hero 块与黄色几何角饰，
 * 替换掉旧蓝紫渐变、毛玻璃分组与圆角覆盖。
 */

/* 弹窗覆写：仅调整内边距布局，让 hero 铺满头部，观感交给全局 */
:deep(.create-app-root .el-dialog__header) { @apply p-0 m-0; }
:deep(.create-app-root .el-dialog__body) { @apply px-6 py-5; }
:deep(.create-app-root .el-dialog__footer) { @apply px-6 pb-5 pt-0; }

/* 头部 Hero：黑底块，替代旧蓝紫渐变横幅 */
.dialog-hero {
  @apply relative px-6 pt-6 pb-5 overflow-hidden;
  background: var(--ink);
}

/* 几何角饰：平面黄色方块 + 黑描边，被 hero 裁切出斜角轮廓 */
.dialog-hero-bg {
  @apply absolute;
  width: 140px; height: 140px; right: -34px; top: -34px;
  background: var(--accent);
  border: 2px solid var(--ink);
  transform: rotate(14deg);
}

.dialog-hero-content { @apply relative z-10 pr-10; }

/* 眉题：黑底上的黄色大写小标签 */
.dialog-eyebrow {
  @apply text-xs tracking-[0.18em] uppercase mb-1.5;
  color: var(--accent);
  font-weight: 800;
}

.dialog-title {
  @apply text-xl mb-1;
  color: var(--paper);
  font-weight: 900;
}

.dialog-desc {
  @apply text-sm;
  color: var(--paper);
  opacity: 0.75;
  font-weight: 600;
}

/* 关闭按钮：黄底黑框直角（覆盖 circle 圆形外观，保持粗野主义直角语言） */
.dialog-close-btn {
  @apply absolute top-4 right-4 z-20;
  background: var(--accent);
  color: var(--ink);
  border: 2px solid var(--ink);
  border-radius: 0;
}
.dialog-close-btn:hover {
  background: var(--paper);
  color: var(--ink);
  border-color: var(--ink);
}

/* 表单 */
.form-body { @apply pt-1; }

/* 分组容器：纸色底 + 细沙线边框，与弹窗暖白表面形成层次 */
.form-section {
  @apply p-4 mb-3;
  background: var(--paper);
  border: 2px solid var(--line-soft);
}

.section-label {
  @apply text-xs tracking-[0.12em] uppercase mb-3;
  color: var(--ink-soft);
  font-weight: 800;
}

.field-label { @apply mr-1; }
.label-help {
  color: var(--ink-soft);
  cursor: help;
}

/* 输入框 + 生成按钮 */
.field-with-action { @apply flex gap-2 w-full; }
.field-control { @apply flex-1; }

/* 提示文字 */
.field-tip {
  @apply mt-2 text-xs leading-5;
  color: var(--ink-soft);
  font-weight: 600;
}

/* 底部按钮：外观由全局主题提供（默认/primary），此处只保留字重强调 */
.dialog-footer { @apply flex justify-end gap-3; }
.footer-btn-primary { font-weight: 800; }
</style>
