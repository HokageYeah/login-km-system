<template>
  <div class="login-container">
    <!-- 装饰背景：粗野主义几何块（平面色块 + 黑边框，替代原模糊光斑） -->
    <div class="background-shapes" aria-hidden="true">
      <div class="shape shape-grid"></div>
      <div class="shape shape-square"></div>
      <div class="shape shape-accent"></div>
      <div class="shape shape-circle"></div>
    </div>

    <!-- 顶部跑马灯：内容从最右侧进场、跑出左侧后再循环 -->
    <div class="top-marquee" aria-hidden="true">
      <div class="marquee-track">
        <span>KM SYSTEM ✦ 授权中心 ✦ 卡密管理 ✦ 设备管控 ✦ 权限校验 ✦ </span>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="card-header">
        <p class="system-kicker">LOGIN / 管理后台</p>
        <h1 class="system-title">卡密管理系统--测试</h1>
        <p class="system-subtitle">高效 · 安全 · 便捷</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <!-- 应用选择框 -->
        <el-form-item prop="app_key">
          <el-select
            v-model="loginForm.app_key"
            placeholder="请选择应用"
            class="custom-input"
            :loading="appsLoading"
          >
            <template #prefix>
              <el-icon class="el-input__icon"><Platform /></el-icon>
            </template>
            <el-option
              v-for="app in appList"
              :key="app.app_key"
              :label="app.app_name"
              :value="app.app_key"
            />
          </el-select>
        </el-form-item>
        <!-- 用户名输入框 -->
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            class="custom-input"
          />
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            class="custom-input"
          />
        </el-form-item>

        <!-- 登录按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '立即登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="card-footer">
        <span class="footer-text">© 2026 KaMi System Admin</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 登录页面组件
 * @description 系统入口，提供用户认证功能。采用科技感设计风格。
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Platform } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 表单引用
const loginFormRef = ref<FormInstance>()
// 加载状态
const loading = ref(false)

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: '',
  app_key: ''
})

// 应用列表数据
const appList = ref<Array<{ app_key: string, app_name: string }>>([])
const appsLoading = ref(false)

/**
 * 表单验证规则
 * @description 用户名至少3位，密码至少6位，必须选择应用
 */
const loginRules = reactive<FormRules>({
  app_key: [
    { required: true, message: '请选择应用', trigger: 'change' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能少于3位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
})

/**
 * 处理登录逻辑
 * @description 验证表单并调用Store的登录Action
 */
const handleLogin = async () => {
    console.log('handleLogin')
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid, fields) => {
    console.log('loginFormRef---valid', valid, fields)
    if (valid) {
      loading.value = true
      try {
        // 获取设备指纹作为device_id
        const { getDeviceId } = await import('@/utils/fingerprint')
        const deviceId = await getDeviceId()
        
        // 调用 User Store 的登录方法
        await userStore.login({
          username: loginForm.username,
          password: loginForm.password,
          app_key: loginForm.app_key,
          device_id: deviceId
        })
        
        ElMessage.success('登录成功，正在跳转...')
        
        // 根据角色跳转
        if (userStore.role === 'admin') {
          router.push('/dashboard')
        } else {
          router.push('/stats') // 普通用户跳转路径，后续可调整
        }
      } catch (error: any) {
        // 错误处理已在 request.ts 中统一处理，此处可做特殊逻辑
        console.error('Login failed:', error)
      } finally {
        loading.value = false
      }
    } else {
      console.log('Form validation failed', fields)
    }
  })
}

/**
 * 获取应用列表
 */
const fetchAppList = async () => {
  appsLoading.value = true
  try {
    const { getPublicApps } = await import('@/api/auth')
    const res = await getPublicApps()
    // 后端返回格式: { total: number, apps: [...] }
    if (res && res.apps) {
      appList.value = res.apps
      // 如果有应用，默认选中第一个
      const [firstApp] = res.apps
      if (firstApp) {
        loginForm.app_key = firstApp.app_key
      }
    }
  } catch (error) {
    console.error('Failed to fetch app list:', error)
    ElMessage.error('获取应用列表失败')
  } finally {
    appsLoading.value = false
  }
}

// 初始化
onMounted(() => {
  fetchAppList()
})
</script>

<style scoped>
/*
 * 登录页（Brutalism 改版）：
 * 纸色底 + 黑框几何装饰 + 硬阴影卡片 + 顶部跑马灯。
 * 表单控件外观统一交给全局 Element Plus 覆盖（styles/index.css），
 * 这里只处理布局与卡片本身，避免与全局主题打架。
 */
.login-container {
  @reference "../../styles/index.css";
  @apply relative w-full h-screen flex justify-center items-center overflow-hidden;
  background: var(--paper);
}

/* 背景装饰：平面几何块（黑描边 + 少量黄色/粉色点缀），无模糊无动画 */
.background-shapes {
  @apply absolute inset-0 overflow-hidden;
}

.shape {
  @apply absolute;
}

/* 细网格：极低对比度，制造"工程图纸"感 */
.shape-grid {
  inset: 0;
  background-image:
    linear-gradient(to right, rgba(20, 20, 20, 0.06) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(20, 20, 20, 0.06) 1px, transparent 1px);
  background-size: 48px 48px;
}

.shape-square {
  @apply w-40 h-40;
  border: 2px solid var(--ink);
  background: var(--accent-blue);
  top: 10%;
  left: 8%;
  transform: rotate(-8deg);
}

.shape-accent {
  @apply w-28 h-28;
  border: 2px solid var(--ink);
  background: var(--accent);
  bottom: 12%;
  right: 10%;
  transform: rotate(12deg);
}

.shape-circle {
  @apply w-36 h-36 rounded-full;
  border: 2px solid var(--ink);
  background: var(--accent-pink);
  top: 14%;
  right: 14%;
}

/* 顶部跑马灯：黑底黄字 */
.top-marquee {
  @apply absolute top-0 left-0 right-0 overflow-hidden;
  background: var(--ink);
  color: var(--accent);
  font-weight: 800;
  font-size: 13px;
  letter-spacing: 0.1em;
  padding: 8px 0;
  border-bottom: 2px solid var(--ink);
}

/* 登录卡片：硬边框 + 大硬阴影 */
.login-card {
  @apply w-full max-w-md p-8 z-10 mx-4;
  background: var(--surface);
  border: 2px solid var(--ink);
  box-shadow: var(--shadow-brutal-lg);
}

.card-header {
  @apply text-center mb-8;
}

/* 眉题：小号大写风格标签 */
.system-kicker {
  @apply text-xs font-extrabold tracking-[0.2em] mb-3;
  color: var(--ink-soft);
}

.system-title {
  @apply text-3xl font-black mb-2 tracking-tight;
  color: var(--ink);
  /* 荧光笔衬底：黄色块从文字下 38% 处垫起 */
  background: linear-gradient(to top, var(--accent) 30%, transparent 30%);
  display: inline-block;
  padding: 0 0.2em;
}

.system-subtitle {
  @apply text-sm font-bold tracking-widest uppercase;
  color: var(--ink-soft);
}

/* 表单布局 */
.login-form {
  @apply space-y-6;
}

/* 登录按钮：全宽加高，按压感由全局 primary 规则提供 */
.login-button {
  @apply w-full h-12 text-lg font-extrabold;
}

.card-footer {
  @apply mt-8 text-center;
}

.footer-text {
  @apply text-xs font-bold;
  color: var(--ink-soft);
}
</style>
