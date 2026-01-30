<template>
  <div class="login-container">
    <!-- 动态背景 -->
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card glass-card">
      <div class="card-header">
        <h1 class="system-title">卡密管理系统</h1>
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
      if (res.apps.length > 0) {
        loginForm.app_key = res.apps[0].app_key
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
/* 容器样式：全屏居中，溢出隐藏 */
.login-container {
  @reference "../../styles/index.css";
  @apply relative w-full h-screen flex justify-center items-center overflow-hidden bg-gray-900;
}

/* 背景图形动画区域 */
.background-shapes {
  @apply absolute inset-0 overflow-hidden;
}

.shape {
  @apply absolute rounded-full filter blur-3xl opacity-30 animate-pulse;
}

.shape-1 {
  @apply w-96 h-96 bg-purple-600 -top-20 -left-20;
  animation-duration: 7s;
}

.shape-2 {
  @apply w-96 h-96 bg-blue-600 top-1/2 right-0 transform -translate-y-1/2 translate-x-1/3;
  animation-duration: 10s;
}

.shape-3 {
  @apply w-80 h-80 bg-pink-600 -bottom-20 left-1/3;
  animation-duration: 8s;
}

/* 登录卡片样式：毛玻璃效果 */
.login-card {
  @apply w-full max-w-md p-8 rounded-2xl z-10 mx-4;
  /* Glassmorphism 样式已在全局 index.css 定义，这里补充特定样式 */
  background: rgba(255, 255, 255, 0.1); /* 深色模式下的玻璃感 */
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.card-header {
  @apply text-center mb-8;
}

.system-title {
  @apply text-3xl font-bold text-white mb-2 tracking-wide;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.system-subtitle {
  @apply text-gray-400 text-sm font-light tracking-widest uppercase;
}

/* 表单样式 */
.login-form {
  @apply space-y-6;
}

/* 自定义输入框样式 */
:deep(.custom-input .el-input__wrapper) {
  @apply bg-white/10 border-none shadow-none rounded-lg h-12 box-border;
  transition: all 0.3s ease;
}

:deep(.custom-input .el-input__wrapper.is-focus) {
  @apply bg-white/20 ring-2 ring-blue-500/50;
}

:deep(.custom-input .el-input__inner) {
  @apply text-white placeholder-gray-400 h-full;
}

:deep(.custom-input .el-input__prefix-inner) {
  @apply text-gray-400;
}

/* 登录按钮样式 */
.login-button {
  @apply w-full h-12 text-lg font-medium rounded-lg border-none;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.login-button:hover {
  @apply opacity-90 shadow-lg transform -translate-y-0.5;
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
}

.login-button:active {
  @apply transform translate-y-0.5;
}

.card-footer {
  @apply mt-8 text-center;
}

.footer-text {
  @apply text-gray-500 text-xs;
}
</style>
